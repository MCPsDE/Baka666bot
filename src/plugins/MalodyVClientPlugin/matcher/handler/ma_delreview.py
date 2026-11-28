"""ma delreview - 删除审核"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.review.delete import delete_review


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    rid = args.strip()
    if not rid:
        await bot.send(event, "用法: ma delreview <审核ID>")
        return
    try:
        await asyncio.to_thread(delete_review, access_token=user["access_token"], uid=uid, review_id=rid)
        await bot.send(event, f"已删除审核 ID:{rid}")
    except Exception:
        await bot.send(event, "删除失败")
