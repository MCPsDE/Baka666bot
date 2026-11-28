"""ma review - 审核列表"""
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
    cid, count = "", 30
    for p in parts:
        if p.isdigit() and len(p) > 2: cid = p
        elif p.isdigit(): count = min(int(p), 100)
    if not cid: await bot.send(event, "用法: ma review <CID> [数量]"); return
    try:
        data, total = await asyncio.to_thread(_paginate, "review/list", {"cid": cid},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"CID:{cid} 暂无审核"); return
        items = [{"status": str(d.get("status","?")), "content": str(d.get("content",""))[:26],
                  "reviewer": d.get("reviewerName","?")[:12]} for d in data]
        img = await list_view(f"CID:{cid} 审核", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"review: {e}"); await bot.send(event, "获取失败")
