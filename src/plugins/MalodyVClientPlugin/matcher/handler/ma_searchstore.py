"""ma searchstore - 商店搜索"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.store.query import query_store
from ...render.components import simple_list


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user or not user.get("store_token"):
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    kw = parts[0] if parts else ""
    page = 1
    for p in parts:
        if p.startswith("p") and p[1:].isdigit():
            page = int(p[1:])
    if not kw:
        await bot.send(event, "用法: ma searchstore <关键词> [p<页码>]")
        return
    try:
        r = await asyncio.to_thread(query_store, store_token=user["store_token"], uid=uid, keyword=kw, limit=50)
        data = r.get("data", [])
        if not data:
            await bot.send(event, "未找到")
            return
        items = [{"title": d.get("title", "?")[:20], "artist": d.get("artist", "?")[:16], "sid": str(d.get("sid", "?")), "bpm": str(d.get("bpm", 0))} for d in data]
        img = await simple_list(f"搜索: {kw}", items, page)
        await bot.send(event, MessageSegment.image(img))
    except Exception:
        await bot.send(event, "搜索失败")
