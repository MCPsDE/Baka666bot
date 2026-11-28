"""ma eventrank - 活动排名"""
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
    parts = args.strip().split()
    if not parts: await bot.send(event, "用法: ma eventrank <EID> [数量]"); return
    eid, count = parts[0], 30
    for p in parts[1:]:
        if p.isdigit(): count = min(int(p), 100)
    try:
        data, total = await asyncio.to_thread(_paginate, "ranking/event", {"eid": eid},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"EID:{eid} 暂无排名"); return
        items = [{"name": d.get("username","?")[:16], "score": str(d.get("score",0)),
                  "idx": str(d.get("index","?"))} for d in data]
        img = await list_view(f"活动 EID:{eid} 排名", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"eventrank: {e}"); await bot.send(event, "获取失败")
