"""ma reviewstatus - 审核状态变更"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.review.status import change_review


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if len(parts) < 2:
        await bot.send(event, "用法: ma reviewstatus <审核ID> <状态>")
        return
    rid, status = parts[0], parts[1]
    try:
        await asyncio.to_thread(change_review, access_token=user["access_token"], uid=uid, review_id=rid, status=status)
        await bot.send(event, f"审核 {rid} 状态已更新为 {status}")
    except Exception:
        await bot.send(event, "更新失败")
