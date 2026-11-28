"""ma addreview - 添加审核"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.review.add import add_review


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split(maxsplit=2)
    if len(parts) < 2:
        await bot.send(event, "用法: ma addreview <CID> <内容> [类型]")
        return
    cid = parts[0]
    content = parts[1] if len(parts) > 1 else ""
    tp = parts[2] if len(parts) > 2 else "0"
    try:
        await asyncio.to_thread(add_review, access_token=user["access_token"], uid=uid, cid=cid, content=content, type_=tp)
        await bot.send(event, f"已提交审核 CID:{cid}")
    except Exception:
        await bot.send(event, "提交失败")
