"""ma activity - 查看玩家动态"""
import asyncio, datetime
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.avtivity import get_player_activity
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
        r = await asyncio.to_thread(get_player_activity, access_token=user["access_token"], uid=uid, touid=touid, limit=10)
        data = r.get("data", [])
        if not data:
            await bot.send(event, f"玩家 {name_hint} 暂无动态")
            return
        lines = [f"玩家 {name_hint} 近期动态:"]
        for item in data[:10]:
            ts = item.get("time", 0)
            tstr = datetime.datetime.fromtimestamp(ts).strftime("%m-%d %H:%M") if ts else "?"
            lines.append(f"  [{tstr}] {item}")
        await bot.send(event, "\n".join(lines[:15]))
    except Exception as e:
        logger.error(f"获取动态失败: {e}")
        await bot.send(event, "获取失败")
