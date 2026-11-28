"""ma reviewcharts - 谱面审核列表"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.review.charts import get_review_charts
from ...render.components import simple_list


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    sid = args.strip()
    if not sid:
        await bot.send(event, "用法: ma reviewcharts <SID>")
        return
    try:
        r = await asyncio.to_thread(get_review_charts, access_token=user["access_token"], uid=uid, sid=sid)
        data = r.get("data", [])
        if not data:
            await bot.send(event, "暂无审核谱面")
            return
        items = [{"cid": str(d.get("cid", "?")), "title": str(d.get("title", "?"))[:20], "version": str(d.get("version", "?"))[:12], "status": str(d.get("status", "?"))} for d in data]
        img = await simple_list(f"SID {sid} 审核谱面", items)
        await bot.send(event, MessageSegment.image(img))
    except Exception:
        await bot.send(event, "获取失败")
