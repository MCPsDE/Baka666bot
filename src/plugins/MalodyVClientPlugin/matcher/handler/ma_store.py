"""ma store - 谱面商店 (1-100 / 100 自动翻页 + 封面图)"""
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
        elif "-" in p:
            parts = p.split("-")
            if parts[0].isdigit() and parts[1].isdigit():
                count = int(parts[1]) - int(parts[0]) + 1; count = min(count, 200)
        elif p.isdigit(): count = int(p)
    mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"][int(mode)] if int(mode) < 8 else f"Mode{mode}"
    try:
        data, total = await asyncio.to_thread(_paginate, "store/list", {"mode": mode},
            access_token=user["store_token"], uid=uid, use_store=True, count=count)
        if not data: await bot.send(event, f"{mn} 暂无谱面"); return
        items = [{"title": d.get("title","?")[:18], "artist": d.get("artist","?")[:14],
                  "sid": str(d.get("sid","?")), "bpm": str(d.get("bpm",0))} for d in data]
        img = await list_view(f"{mn} 谱面商店", items, f"共 {total} 条 | 输入 1-200 获取更多")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"store: {e}"); await bot.send(event, "获取失败")
