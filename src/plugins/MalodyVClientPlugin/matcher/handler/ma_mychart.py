"""ma mychart - 我的谱面 (通过 player/chart API + 自动翻页)"""
import asyncio
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
    touid, count, name_hint = uid, 30, user.get("username", uid)
    for p in args.strip().split():
        if p.isdigit(): touid = p
        elif p:
            try:
                r = await asyncio.to_thread(search_player, keyword=p, access_token=user["access_token"], uid=uid, limit=1)
                d = r.get("data", [])
                if d and d[0].get("uid"): touid = str(d[0]["uid"]); name_hint = d[0].get("username", touid)
            except: pass
    try:
        data, total = await asyncio.to_thread(_paginate, "community/player/chart", {"touid": touid},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"{name_hint} 暂无谱面"); return
        items = [{"title": d.get("title","?")[:18], "version": str(d.get("version","?"))[:14],
                  "cid": str(d.get("cid","?")), "level": str(d.get("level","?"))} for d in data]
        img = await list_view(f"{name_hint} 的谱面", items, f"共 {total} 个")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"mychart: {e}"); await bot.send(event, "获取失败")
