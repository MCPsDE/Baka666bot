"""ma event - 活动列表"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.core import _paginate
from ...render.components import list_view

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user or not user.get("store_token"):
        await bot.send(event, BIND_GUIDE_TEXT); return
    count = 30
    for p in args.strip().split():
        if p.isdigit(): count = min(int(p), 100)
    try:
        data, total = await asyncio.to_thread(_paginate, "store/events", {},
            access_token=user["store_token"], uid=uid, use_store=True, count=count)
        if not data: await bot.send(event, "暂无活动"); return
        items = [{"name": d.get("name","?")[:18], "sponsor": d.get("sponsor","")[:12],
                  "active": "进行中" if d.get("active") else "已结束", "eid": str(d.get("eid","?"))} for d in data]
        img = await list_view("活动列表", items, f"共 {total} 个")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"event: {e}"); await bot.send(event, "获取失败")
