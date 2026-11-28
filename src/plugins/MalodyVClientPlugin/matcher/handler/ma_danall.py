"""ma danall - 全段位列表"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.dan.all import get_all_dan
from ...render.components import list_view

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    mode = "0"
    for p in args.strip().split():
        if p.isdigit() and len(p) == 1: mode = p
    mn = ["Key","Step","DJ","Catch","Pad","Taiko","Ring","Slide"][int(mode)] if int(mode) < 8 else f"Mode{mode}"
    try:
        r = await asyncio.to_thread(get_all_dan, access_token=user["access_token"], uid=uid, mode=mode)
        data = r.get("data", [])
        if not data: await bot.send(event, f"{mn} 暂无段位"); return
        items = [{"dan": d.get("danName","?")[:18], "rate": f"{d.get('rate',0):.1f}%", "success": str(d.get("success",0))} for d in data]
        img = await list_view(f"{mn} 全段位", items, f"共 {len(data)} 项")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"danall: {e}"); await bot.send(event, "获取失败")
