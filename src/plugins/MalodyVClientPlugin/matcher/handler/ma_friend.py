"""ma friend - 好友列表 (自动翻页)"""
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
    count = 100
    for p in args.strip().split():
        if p.isdigit(): count = min(int(p), 200)
    try:
        data, total = await asyncio.to_thread(_paginate, "player/friend", {},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, "好友列表为空"); return
        items = [{"username": d.get("username","?")[:20], "uid": str(d.get("uid","?"))} for d in data]
        img = await list_view("好友列表", items, f"共 {total} 人")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"friend: {e}"); await bot.send(event, "获取失败")
