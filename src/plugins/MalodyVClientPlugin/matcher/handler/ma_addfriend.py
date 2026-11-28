"""ma addfriend - 添加好友"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.friend.toggle import toggle_friend


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    target = args.strip()
    if not target or not target.isdigit():
        await bot.send(event, "用法: ma addfriend <UID>")
        return
    try:
        r = await asyncio.to_thread(toggle_friend, access_token=user["access_token"], uid=uid, target_uid=target, add=True)
        if r.get("code") == 0:
            await bot.send(event, f"已添加好友 UID:{target}")
        else:
            await bot.send(event, f"操作失败: {r.get('message','?')}")
    except Exception as e:
        logger.error(f"添加好友失败: {e}")
        await bot.send(event, "操作失败")
