"""ma wiki - Wiki 查询"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.wiki import get_wiki


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return

    parts = args.strip().split()
    sid = None
    cid = None
    for p in parts:
        if p.upper().startswith("S"):
            sid = p[1:]
        elif p.upper().startswith("C"):
            cid = p[1:]
        elif p.isdigit():
            if not sid:
                sid = p
            elif not cid:
                cid = p

    if not sid and not cid:
        await bot.send(event, "用法: ma wiki <SID> [CID]  或  ma wiki S12345 C67890")
        return

    try:
        result = await asyncio.to_thread(
            get_wiki, access_token=user["access_token"], uid=uid, sid=sid, cid=cid
        )
        wiki_text = result.get("wiki", "")
        if not wiki_text:
            await bot.send(event, "该条目暂无 Wiki 内容")
            return
        # 截断过长内容
        if len(wiki_text) > 500:
            wiki_text = wiki_text[:497] + "..."
        await bot.send(event, f"Wiki (SID:{sid or '?'} CID:{cid or '?'}):\n{wiki_text}")
    except Exception as e:
        logger.error(f"获取 Wiki 失败: {e}")
        await bot.send(event, "获取 Wiki 失败")
