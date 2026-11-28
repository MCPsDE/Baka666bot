"""ma mute - 屏蔽玩家（二次确认）"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.mute import set_mute


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if not parts:
        await bot.send(event, "用法: ma mute <UID> [confirm]")
        return
    target = parts[0]
    if len(parts) < 2 or parts[1] != "confirm":
        await bot.send(event, f"确认屏蔽 UID:{target}？输入 ma mute {target} confirm 确认")
        return
    try:
        await asyncio.to_thread(set_mute, access_token=user["access_token"], uid=uid, target_uid=target, mute=True)
        await bot.send(event, f"已屏蔽 UID:{target}")
    except Exception:
        await bot.send(event, "操作失败")
