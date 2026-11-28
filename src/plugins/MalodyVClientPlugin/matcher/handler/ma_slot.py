"""ma slot - 插槽数据"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.slot import set_chart_slot


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if len(parts) < 3:
        await bot.send(event, "用法: ma slot <模式> <slot1> [slot2] ...")
        return
    mode = parts[0]
    slots = parts[1:]
    try:
        await asyncio.to_thread(set_chart_slot, access_token=user["access_token"], uid=uid, mode=mode, slots=slots)
        await bot.send(event, f"Slot 已更新 Mode:{mode}")
    except Exception:
        await bot.send(event, "更新失败")
