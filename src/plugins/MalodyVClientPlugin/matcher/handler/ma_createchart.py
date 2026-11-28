"""ma createchart - 创建谱面"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.create import create_chart


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if len(parts) < 4:
        await bot.send(event, "用法: ma createchart <SID> <版本名> <模式> <等级> [长度] [类型]")
        return
    sid, version, mode, level = parts[0], parts[1], parts[2], parts[3]
    length = parts[4] if len(parts) > 4 else "0"
    type_ = parts[5] if len(parts) > 5 else "0"
    try:
        r = await asyncio.to_thread(create_chart, access_token=user["access_token"], uid=uid, sid=sid, version=version, mode=mode, level=level, length=length, type_=type_)
        cid = r.get("cid", "?")
        await bot.send(event, f"谱面创建成功！CID: {cid} SID: {r.get('sid','?')}")
    except Exception as e:
        await bot.send(event, f"创建失败")
