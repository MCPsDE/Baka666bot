"""ma reviewqueue - 审核队列"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.core import _paginate
from ...render.components import list_view

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    mode, count = "0", 20
    for p in args.strip().split():
        if p.isdigit() and len(p) == 1: mode = p
        elif p.isdigit(): count = min(int(p), 50)
    try:
        data, total = await asyncio.to_thread(_paginate, "review/queue", {"mode": mode},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, "审核队列为空"); return
        items = [{"title": d.get("title","?")[:18], "artist": d.get("artist","?")[:12],
                  "count": str(d.get("count",0)), "sid": str(d.get("sid","?"))} for d in data]
        img = await list_view("审核队列", items, f"共 {total} 项")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"reviewqueue: {e}"); await bot.send(event, "获取失败")
