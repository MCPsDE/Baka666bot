"""ma chartlist - 歌曲谱面列表"""
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
    parts = args.strip().split()
    sid, mode, count = "", "0", 50
    for p in parts:
        if p.isdigit() and len(p) == 1: mode = p
        elif p.isdigit() and len(p) > 2: sid = p
        elif p.isdigit(): count = min(int(p), 100)
    if not sid: await bot.send(event, "用法: ma chartlist <SID> [模式]"); return
    try:
        data, total = await asyncio.to_thread(_paginate, "store/charts", {"sid": sid, "mode": mode},
            access_token=user["store_token"], uid=uid, use_store=True, count=count)
        if not data: await bot.send(event, f"SID:{sid} 暂无谱面"); return
        items = [{"version": str(d.get("version","?"))[:14], "level": str(d.get("level","")),
                  "creator": d.get("creator","?")[:12], "cid": str(d.get("cid","?")),
                  "type": str(d.get("type",""))} for d in data]
        img = await list_view(f"SID:{sid} 谱面", items, f"共 {total} 个")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"chartlist: {e}"); await bot.send(event, "获取失败")
