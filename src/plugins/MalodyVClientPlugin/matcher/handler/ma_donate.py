"""ma donate - 赞助谱面"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.donate import donate_chart


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if len(parts) < 2:
        await bot.send(event, "用法: ma donate <CID> <金币数>")
        return
    cid, gold = parts[0], parts[1]
    try:
        r = await asyncio.to_thread(donate_chart, access_token=user["access_token"], uid=uid, cid=cid, gold=int(gold))
        await bot.send(event, f"已赞助 CID:{cid} {gold}金币")
    except Exception:
        await bot.send(event, "赞助失败")
