"""ma friendstore - 好友商店"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.store.friend import get_friend_store
from ...render.components import simple_list


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user or not user.get("store_token"):
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    page = 1
    for p in args.strip().split():
        if p.startswith("p") and p[1:].isdigit():
            page = int(p[1:])
    try:
        r = await asyncio.to_thread(get_friend_store, store_token=user["store_token"], uid=uid, limit=50)
        data = r.get("data", [])
        if not data:
            await bot.send(event, "好友商店暂无内容")
            return
        items = [{"title": d.get("title", "?")[:20], "artist": d.get("artist", "?")[:16], "sid": str(d.get("sid", "?")), "bpm": str(d.get("bpm", 0))} for d in data]
        img = await simple_list("好友商店", items, page)
        await bot.send(event, MessageSegment.image(img))
    except Exception:
        await bot.send(event, "获取失败")
