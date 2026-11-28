"""ma promote - 推广列表"""
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
    count = 50
    for p in args.strip().split():
        if p.isdigit(): count = min(int(p), 200)
    try:
        data, total = await asyncio.to_thread(_paginate, "store/promote", {},
            access_token=user["store_token"], uid=uid, use_store=True, count=count)
        if not data: await bot.send(event, "暂无推广"); return
        items = [{"title": d.get("title","?")[:18], "artist": d.get("artist","?")[:14],
                  "sid": str(d.get("sid","?"))} for d in data]
        img = await list_view("推广列表", items, f"共 {total} 项")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"promote: {e}"); await bot.send(event, "获取失败")
