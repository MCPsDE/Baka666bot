import asyncio
import re
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger

from ...MalodyAPI.ranking.best import get_best
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.search import search_player
from ...MalodyAPI.player.info import get_player_info
from ...MalodyAPI.ranking.player.all import get_ranking_player_all
from ...render.mmbest import draw_malody_bp


async def resolve_uid(keyword: str, access_token: str, uid: str) -> str | None:
    """通过关键词解析出目标 UID。纯数字直接返回，否则调用搜索 API。"""
    if keyword.isdigit():
        return keyword
    try:
        result = await asyncio.to_thread(
            search_player,
            keyword=keyword,
            access_token=access_token,
            uid=uid,
            limit=1,
        )
        data = result.get("data", [])
        if data and data[0].get("uid"):
            return str(data[0]["uid"])
    except Exception as e:
        logger.error(f"搜索玩家 {keyword} 失败: {e}")
    return None


async def get_user_profile(touid: str, mode: str, access_token: str, uid: str):
    """
    获取玩家展示信息。
    返回: (user_name, avatar_url, rank_text, mode_stats)
    """
    try:
        info = await asyncio.to_thread(
            get_player_info,
            touid=touid,
            access_token=access_token,
            uid=uid,
        )
        user_name = info.get("username")
        avatar = info.get("avatar")
        avatar_url = f"https://cni.machart.top/avatar/{avatar}" if avatar else None
    except Exception as e:
        logger.error(f"获取玩家 {touid} 信息失败: {e}")
        return None, None, None, None

    # 获取排名信息（可选）
    rank_text = None
    mode_stats = None
    try:
        all_rank = await asyncio.to_thread(
            get_ranking_player_all,
            touid=touid,
            access_token=access_token,
            uid=uid,
        )
        for item in all_rank.get("data", []):
            if str(item.get("mode")) == mode:
                rank_text = f"#{item.get('rank', '?')}"
                mode_stats = {
                    "exp": str(item.get("level", 0)),
                    "playcount": str(item.get("pc", 0)),
                    "acc": f"{item.get('acc', 0):.2f}%",
                    "combo": str(item.get("combo", 0)),
                }
                break
    except Exception as e:
        logger.error(f"获取玩家 {touid} 排名失败: {e}")

    return user_name, avatar_url, rank_text, mode_stats


def _is_param_token(token: str) -> bool:
    """判断 token 是模式、范围还是精度参数（而非玩家关键词）"""
    # 模式: 单个数字 0-7
    if token.isdigit() and len(token) == 1:
        return True
    # 范围: 如 1-50, 5-10
    if re.fullmatch(r'\d+-\d+', token):
        return True
    # 精度: .2f, .4f 等
    if re.fullmatch(r'\.\d+f', token):
        return True
    return False


async def process_best(bot: Bot, event: Event, args: str):
    """处理 /mb 命令，查询 best 成绩并发送图片。支持查询自己或指定玩家。"""
    qq = str(event.get_user_id())
    user_uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return

    plain = args.strip().split()

    # 默认参数
    keyword = None
    mode = "0"
    limit_start = 0
    limit_end = 100
    precision = 2

    # 解析参数：判断第一个 token 是玩家关键词还是模式/范围/精度
    if not plain:
        # 无参数，查询自己
        touid = user_uid
    else:
        first = plain[0]
        if _is_param_token(first):
            # 第一个 token 是参数，省略了玩家，查询自己
            touid = user_uid
            param_start_idx = 0
        else:
            # 第一个 token 是玩家关键词
            keyword = first
            param_start_idx = 1

        # 解析参数（从 param_start_idx 开始）
        for arg in plain[param_start_idx:]:
            if arg.isdigit() and len(arg) == 1:
                mode = arg
            elif '-' in arg:
                parts = arg.split('-')
                if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                    limit_start = max(0, int(parts[0]) - 1)
                    limit_end = min(100, int(parts[1]))
            elif arg.isdigit() and len(arg) > 1:
                limit_end = min(100, int(arg))
            elif arg.startswith('.') and arg.endswith('f') and arg[1:-1].isdigit():
                precision = int(arg[1:-1])

        # 如果有 keyword，解析成 UID
        if keyword:
            touid = await resolve_uid(keyword, user["access_token"], user_uid)
            if not touid:
                await bot.send(event, "未找到该玩家")
                return
        else:
            touid = user_uid

    mode_map = {
        "0": "Key", "1": "Step", "2": "DJ", "3": "Catch",
        "4": "Pad", "5": "Taiko", "6": "Ring", "7": "Slide"
    }
    mode_name = mode_map.get(mode, f"Mode {mode}")

    user_name, avatar_url, rank_text, mode_stats = await get_user_profile(
        touid, mode, user["access_token"], user_uid
    )
    display_name = user_name if user_name else touid
    logger.info(f"查询 {display_name} 的 {mode_name} 模式 Best 成绩...")

    records = []
    has_more = True
    next_from = 0
    max_pages = (limit_end + 19) // 20 + 2

    try:
        while has_more and len(records) < limit_end and max_pages > 0:
            max_pages -= 1
            result = await asyncio.to_thread(
                get_best,
                access_token=user["access_token"],
                uid=user_uid,
                touid=touid,
                mode=mode,
                from_=next_from,
                limit=limit_end,
            )
            page_data = result.get("data", [])
            if not page_data:
                break
            records.extend(page_data)
            has_more = result.get("hasMore", False)
            next_from = result.get("next", 0)
            if not has_more or next_from == 0:
                break

        if not records:
            await bot.send(event, f"玩家 {display_name} 在 {mode_name} 模式下没有成绩。")
            return

        final_records = records[limit_start:limit_end]
        if not final_records:
            await bot.send(event, "指定范围内的成绩不存在。")
            return

        range_display = f"{limit_start + 1}-{limit_end}"
        img_bytes = await draw_malody_bp(
            touid, mode_name, final_records,
            user_name=user_name, avatar_url=avatar_url,
            rank_text=rank_text, mode_stats=mode_stats,
            precision=precision,
            range_display=range_display,
        )
        await bot.send(event, MessageSegment.image(img_bytes))

    except Exception as e:
        logger.error(f"Best 查询异常: {e}")
        await bot.send(event, "查询失败，请稍后重试")