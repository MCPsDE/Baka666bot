"""ma chartpromote - 推广谱面（二次确认）"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.promote import set_chart_promote


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if not parts:
        await bot.send(event, "用法: ma chartpromote <CID> [confirm]")
        return
    cid = parts[0]
    if len(parts) < 2 or parts[1] != "confirm":
        await bot.send(event, f"确认推广 CID:{cid}？操作将消耗金币。输入 ma chartpromote {cid} confirm 确认")
        return
    try:
        await asyncio.to_thread(set_chart_promote, access_token=user["access_token"], uid=uid, cid=cid, promote=True)
        await bot.send(event, f"已推广 CID:{cid}")
    except Exception:
        await bot.send(event, "推广失败")
