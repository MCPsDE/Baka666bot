"""ma achieve - 成就列表"""
import asyncio, datetime
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.achieve.player.all import get_achieve
from ...MalodyAPI.player.search import search_player
from ...render.components import list_view

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    touid, name_hint = uid, user.get("username", uid)
    if args.strip():
        kw = args.strip()
        if kw.isdigit(): touid = kw
        else:
            try:
                r = await asyncio.to_thread(search_player, keyword=kw, access_token=user["access_token"], uid=uid, limit=1)
                d = r.get("data", [])
                if d and d[0].get("uid"): touid = str(d[0]["uid"]); name_hint = d[0].get("username", touid)
            except: pass
    try:
        data = await asyncio.to_thread(get_achieve, access_token=user["access_token"], uid=uid, touid=touid)
        items_raw = data.get("data", [])
        if not items_raw: await bot.send(event, f"{name_hint} 暂无成就"); return
        items = [{"name": d.get("name","?")[:24], "time": datetime.datetime.fromtimestamp(d.get("time",0)).strftime("%Y-%m-%d") if d.get("time") else "?"} for d in items_raw]
        img = await list_view(f"{name_hint} 成就", items, f"共 {len(items_raw)} 项")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"achieve: {e}"); await bot.send(event, "获取失败")
