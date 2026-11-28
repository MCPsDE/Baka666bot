"""ma like - 点赞谱面"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.like import like_chart


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    cid = args.strip()
    if not cid or not cid.isdigit():
        await bot.send(event, "用法: ma like <CID>")
        return
    try:
        r = await asyncio.to_thread(like_chart, access_token=user["access_token"], uid=uid, cid=cid, like=True)
        if r.get("code") == 0:
            await bot.send(event, f"已点赞 CID:{cid}")
        else:
            await bot.send(event, "操作失败")
    except Exception as e:
        logger.error(f"点赞失败: {e}")
        await bot.send(event, "操作失败")
