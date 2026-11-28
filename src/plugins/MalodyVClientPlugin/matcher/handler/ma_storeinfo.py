"""ma storeinfo - 商店信息"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.store.info import get_store_info
from ...render.components import simple_card


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user or not user.get("store_token"):
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    try:
        r = await asyncio.to_thread(get_store_info, store_token=user["store_token"], uid=uid)
        rows = [("API版本", str(r.get("api", "?"))), ("最低版本", str(r.get("min", "?"))), ("欢迎信息", str(r.get("welcome", ""))[:60])]
        img = await simple_card("商店信息", rows)
        await bot.send(event, __import__("nonebot.adapters.onebot.v11").MessageSegment.image(img))
    except Exception:
        await bot.send(event, "获取失败")
