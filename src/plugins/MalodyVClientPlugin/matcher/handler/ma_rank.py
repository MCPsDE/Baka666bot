"""ma rank - 查看段位信息"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.ranking.player.all import get_ranking_player_all
from ...MalodyAPI.player.search import search_player


MODE_NAMES = ["Key", "Step", "DJ", "Catch", "Pad", "Taiko", "Ring", "Slide"]


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return

    touid = uid
    name_hint = user.get("username", uid)
    if args.strip():
        keyword = args.strip().split()[0]
        if keyword.isdigit():
            touid = keyword
        else:
            try:
                result = await asyncio.to_thread(
                    search_player, keyword=keyword, access_token=user["access_token"], uid=uid, limit=1
                )
                data = result.get("data", [])
                if data and data[0].get("uid"):
                    touid = str(data[0]["uid"])
                    name_hint = data[0].get("username", touid)
                else:
                    await bot.send(event, "未找到该玩家")
                    return
            except Exception as e:
                logger.error(f"搜索失败: {e}")
                await bot.send(event, "搜索失败")
                return

    try:
        result = await asyncio.to_thread(
            get_ranking_player_all, touid=touid, access_token=user["access_token"], uid=uid
        )
        data = result.get("data", [])
        if not data:
            await bot.send(event, f"玩家 {name_hint} 暂无排名信息")
            return
        lines = [f"玩家 {name_hint} 段位信息:"]
        for item in data:
            mode_idx = item.get("mode", 0)
            mode_name = MODE_NAMES[mode_idx] if mode_idx < len(MODE_NAMES) else f"Mode{mode_idx}"
            rank = item.get("rank", "?")
            level = item.get("level", "?")
            pc = item.get("pc", 0)
            acc = item.get("acc", 0)
            combo = item.get("combo", 0)
            lines.append(f"  [{mode_name}] Rank:{rank} Lv.{level} PC:{pc} Acc:{acc:.2f}% Combo:{combo}")
        await bot.send(event, "\n".join(lines[:12]))
    except Exception as e:
        logger.error(f"获取排名失败: {e}")
        await bot.send(event, "获取排名失败")
