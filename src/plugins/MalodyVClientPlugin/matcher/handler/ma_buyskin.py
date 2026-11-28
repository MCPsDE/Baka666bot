"""ma buyskin - 购买皮肤（二次确认）"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.skin.buy import buy_skin


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user or not user.get("store_token"):
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split()
    if not parts:
        await bot.send(event, "用法: ma buyskin <ID> [confirm]")
        return
    sid = parts[0]
    if len(parts) < 2 or parts[1] != "confirm":
        await bot.send(event, f"确认购买皮肤 ID:{sid}？将消耗金币。输入 ma buyskin {sid} confirm 确认")
        return
    try:
        r = await asyncio.to_thread(buy_skin, store_token=user["store_token"], uid=uid, skin_id=sid)
        await bot.send(event, f"购买成功！{r.get('data',{}).get('name','')}")
    except Exception:
        await bot.send(event, "购买失败")
