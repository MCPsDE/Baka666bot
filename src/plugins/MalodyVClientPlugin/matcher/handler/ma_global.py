"""ma global - 全球排名"""
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
    mode, type_, count = "0", "pc", 30
    for p in args.strip().split():
        if p.isdigit() and len(p) == 1: mode = p
        elif p in ("pc","score","combo","acc"): type_ = p
        elif p.isdigit(): count = min(int(p), 100)
    mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"][int(mode)] if int(mode) < 8 else f"Mode{mode}"
    tn = {"pc":"游玩次数","score":"分数","combo":"连击","acc":"准确率"}.get(type_, type_)
    try:
        data, total = await asyncio.to_thread(_paginate, "ranking/global", {"mode": mode, "type": type_},
            access_token=user["access_token"], uid=uid, count=count)
        if not data: await bot.send(event, f"{mn} 暂无全球排名"); return
        items = [{"rank": str(d.get("rank","?")), "name": d.get("username","?")[:14],
                  "value": str(d.get("value",0))} for d in data]
        img = await list_view(f"{mn} 全球排名 ({tn})", items, f"共 {total} 条")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"global: {e}"); await bot.send(event, "获取失败")
