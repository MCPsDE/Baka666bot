"""ma puzzle - 查看拼图进度"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.puzzle.player.all import get_puzzle
from ...MalodyAPI.player.search import search_player


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    touid = uid
    name_hint = user.get("username", uid)
    if args.strip():
        kw = args.strip()
        if kw.isdigit():
            touid = kw
        else:
            try:
                r = await asyncio.to_thread(search_player, keyword=kw, access_token=user["access_token"], uid=uid, limit=1)
                d = r.get("data", [])
                if d and d[0].get("uid"):
                    touid = str(d[0]["uid"])
                    name_hint = d[0].get("username", touid)
            except Exception:
                pass
    try:
        r = await asyncio.to_thread(get_puzzle, access_token=user["access_token"], uid=uid, touid=touid)
        data = r.get("data", [])
        if not data:
            await bot.send(event, f"玩家 {name_hint} 暂无拼图数据")
            return
        await bot.send(event, f"玩家 {name_hint} 拼图进度: {data}")
    except Exception as e:
        logger.error(f"获取拼图失败: {e}")
        await bot.send(event, "获取失败")
