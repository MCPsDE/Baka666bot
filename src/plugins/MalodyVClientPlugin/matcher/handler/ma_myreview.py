"""ma myreview - 我的审核"""
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
    count = 30
    for p in args.strip().split():
        if p.isdigit(): count = min(int(p), 50)
    try:
        data, total = await asyncio.to_thread(_paginate, "review/my", {},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, "暂无提交审核"); return
        items = [{"title": d.get("title","?")[:18], "version": str(d.get("version","?"))[:12],
                  "status": str(d.get("status","?")), "cid": str(d.get("cid","?"))} for d in data]
        img = await list_view("我的审核", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"myreview: {e}"); await bot.send(event, "获取失败")
