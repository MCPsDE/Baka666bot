"""ma reviewaction - 审核操作"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.review.action import review_action


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split(maxsplit=2)
    if len(parts) < 2:
        await bot.send(event, "用法: ma reviewaction <chart_id> <action> [comment]")
        return
    chart_id, action = parts[0], parts[1]
    comment = parts[2] if len(parts) > 2 else ""
    try:
        await asyncio.to_thread(review_action, access_token=user["access_token"], uid=uid, chart_id=chart_id, action=action, comment=comment)
        await bot.send(event, f"审核操作完成: {action}")
    except Exception:
        await bot.send(event, "操作失败")
