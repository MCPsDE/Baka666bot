"""ma skincheck - 检查皮肤"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.skin.check import check_skin
from ...render.components import simple_card


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user or not user.get("store_token"):
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    h = args.strip()
    if not h:
        await bot.send(event, "用法: ma skincheck <hash>")
        return
    try:
        r = await asyncio.to_thread(check_skin, store_token=user["store_token"], uid=uid, skin_hash=h)
        rows = [(k, str(v)[:60]) for k, v in r.items() if k != "code"]
        img = await simple_card(f"皮肤检查: {h[:20]}", rows)
        await bot.send(event, __import__("nonebot.adapters.onebot.v11").MessageSegment.image(img))
    except Exception:
        await bot.send(event, "检查失败")
