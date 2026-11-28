"""ma comment - 评论列表 (自动翻页)"""
import asyncio, datetime
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
    cid, count = "", 50
    for p in parts:
        if p.isdigit() and len(p) > 1: cid = p
        elif p.isdigit(): count = min(int(p), 100)
    if not cid: await bot.send(event, "用法: ma comment <CID> [数量]"); return
    try:
        data, total = await asyncio.to_thread(_paginate, "comment/list", {"cid": cid},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"CID:{cid} 暂无评论"); return
        items = [{"name": d.get("name","?")[:12], "content": str(d.get("content",""))[:26],
                  "time": datetime.datetime.fromtimestamp(d.get("time",0)).strftime("%m-%d") if d.get("time") else "?"} for d in data]
        img = await list_view(f"CID:{cid} 评论", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"comment: {e}"); await bot.send(event, "获取失败")
