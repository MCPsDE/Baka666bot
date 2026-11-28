"""ma chartrank - 谱面排行榜"""
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
    if not parts: await bot.send(event, "用法: ma chartrank <CID> [模式]"); return
    cid, mode, count = parts[0], "0", 30
    for p in parts[1:]:
        if p.isdigit() and len(p) == 1: mode = p
        elif p.isdigit(): count = min(int(p), 100)
    mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"][int(mode)] if int(mode) < 8 else f"Mode{mode}"
    try:
        data, total = await asyncio.to_thread(_paginate, "ranking/list", {"cid": cid, "mode": mode},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"CID:{cid} {mn} 暂无排行"); return
        items = [{"rank": str(d.get("ranking","?")), "name": d.get("username","?")[:14],
                  "score": str(d.get("score",0)), "acc": f"{d.get('acc',0):.2f}%"} for d in data]
        img = await list_view(f"CID:{cid} {mn} 排行", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"chartrank: {e}"); await bot.send(event, "获取失败")
