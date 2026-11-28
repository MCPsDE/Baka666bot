"""ma addcomment - 发表评论"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.comment.add import add_comment


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        await bot.send(event, "用法: ma addcomment <CID> <内容>")
        return
    cid, content = parts[0], parts[1]
    try:
        await asyncio.to_thread(add_comment, access_token=user["access_token"], uid=uid, cid=cid, content=content)
        await bot.send(event, f"已评论 CID:{cid}")
    except Exception:
        await bot.send(event, "评论失败")
