"""ma quest - 任务列表"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.quest.list import get_quest
from ...render.components import list_view

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    try:
        r = await asyncio.to_thread(get_quest, access_token=user["access_token"], uid=uid)
        data = r.get("data", [])
        if not data: await bot.send(event, "暂无任务"); return
        items = [{"name": d.get("name","?")[:18], "status": "完成" if d.get("status")==1 else "进行中",
                  "percent": f"{d.get('percent',0):.0f}%", "award": str(d.get("award",""))[:14]} for d in data]
        img = await list_view("当前任务", items, f"共 {len(data)} 个")
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"quest: {e}"); await bot.send(event, "获取失败")
