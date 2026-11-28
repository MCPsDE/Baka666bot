"""ma delcomment - 删除评论"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.comment.delete import delete_comment


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    tid = args.strip()
    if not tid or not tid.isdigit():
        await bot.send(event, "用法: ma delcomment <评论ID>")
        return
    try:
        await asyncio.to_thread(delete_comment, access_token=user["access_token"], uid=uid, tid=tid)
        await bot.send(event, f"已删除评论 TID:{tid}")
    except Exception:
        await bot.send(event, "删除失败")
