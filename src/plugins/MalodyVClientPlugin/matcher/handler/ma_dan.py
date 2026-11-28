"""ma dan - 段位记录 (自动翻页)"""
import asyncio, datetime
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.core import _paginate
from ...MalodyAPI.player.search import search_player
from ...render.components import list_view

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    touid, mode, count, name_hint = uid, "0", 50, user.get("username", uid)
    for p in args.strip().split():
        if p.isdigit() and len(p) == 1: mode = p
        elif p.isdigit(): touid = p
        elif p:
            try:
                r = await asyncio.to_thread(search_player, keyword=p, access_token=user["access_token"], uid=uid, limit=1)
                d = r.get("data", [])
                if d and d[0].get("uid"): touid = str(d[0]["uid"]); name_hint = d[0].get("username", touid)
            except: pass
    mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"][int(mode)] if int(mode) < 8 else f"Mode{mode}"
    try:
        data, total = await asyncio.to_thread(_paginate, "dan/list", {"touid": touid, "mode": mode},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"{name_hint} 暂无 {mn} 段位"); return
        items = [{"dan": d.get("danName","?")[:16], "rank": str(d.get("rank","?")),
                  "rate": f"{d.get('rate',0):.1f}%", "time": datetime.datetime.fromtimestamp(d.get("time",0)).strftime("%Y-%m") if d.get("time") else "?"} for d in data]
        img = await list_view(f"{name_hint} {mn} 段位", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"dan: {e}"); await bot.send(event, "获取失败")
