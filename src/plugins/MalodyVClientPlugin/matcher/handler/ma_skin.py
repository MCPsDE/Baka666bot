"""ma skin - 皮肤列表 (自动翻页)"""
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
    mode, count = "0", 50
    for p in args.strip().split():
        if p.isdigit() and len(p) == 1: mode = p
        elif p.isdigit(): count = min(int(p), 200)
    mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"][int(mode)] if int(mode) < 8 else f"Mode{mode}"
    try:
        data, total = await asyncio.to_thread(_paginate, "skin/list", {"mode": mode},
            access_token=user["store_token"], uid=uid, use_store=True, count=count)
        if not data: await bot.send(event, f"{mn} 暂无皮肤"); return
        items = [{"name": s.get("name","?")[:18], "creator": s.get("creator","?")[:14],
                  "hot": str(s.get("hot",0)), "price": str(s.get("price",0))} for s in data]
        img = await list_view(f"{mn} 皮肤列表", items, f"共 {total} 个")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"skin: {e}"); await bot.send(event, "获取失败")
