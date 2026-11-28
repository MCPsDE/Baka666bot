"""ma settype - 设置谱面类型"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.type import set_chart_type


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if len(parts) < 2:
        await bot.send(event, "用法: ma settype <CID> <类型>")
        return
    cid, tp = parts[0], parts[1]
    try:
        await asyncio.to_thread(set_chart_type, access_token=user["access_token"], uid=uid, cid=cid, type_=tp)
        await bot.send(event, f"已设置 CID:{cid} 类型为 {tp}")
    except Exception:
        await bot.send(event, "设置失败")
