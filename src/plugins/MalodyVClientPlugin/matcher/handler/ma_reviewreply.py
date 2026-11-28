"""ma reviewreply - 审核回复"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.review.reply import get_review_reply, add_review_reply
from ...render.components import simple_list


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split(maxsplit=1)
    if not parts:
        await bot.send(event, "用法: ma reviewreply <issue_id> [回复内容]")
        return
    issue_id = parts[0]
    reply_content = parts[1] if len(parts) > 1 else ""
    if reply_content:
        try:
            await asyncio.to_thread(add_review_reply, access_token=user["access_token"], uid=uid, issue_id=issue_id, content=reply_content)
            await bot.send(event, "已回复")
            return
        except Exception:
            await bot.send(event, "回复失败")
            return
    try:
        r = await asyncio.to_thread(get_review_reply, access_token=user["access_token"], uid=uid, issue_id=issue_id)
        data = r.get("data", [])
        if not data:
            await bot.send(event, "暂无回复")
            return
        items = [{"user": str(d.get("userName", "?"))[:14], "content": str(d.get("content", ""))[:30]} for d in data]
        img = await simple_list(f"审核回复 Issue#{issue_id}", items)
        await bot.send(event, MessageSegment.image(img))
    except Exception:
        await bot.send(event, "获取失败")
