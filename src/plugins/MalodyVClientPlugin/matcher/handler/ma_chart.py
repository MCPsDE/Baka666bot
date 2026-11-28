"""ma chart - 谱面信息 (含封面)"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.info import get_chart_info
from ...render.components import chart_card

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    cid = args.strip()
    if not cid or not cid.isdigit(): await bot.send(event, "用法: ma chart <CID>"); return
    try:
        r = await asyncio.to_thread(get_chart_info, access_token=user["access_token"], uid=uid, cid=cid)
        sid = str(r.get("sid","?"))
        cover = f"https://cni.machart.top/cover/{sid}!small" if r.get("sid") else None
        mode_map = {0:"Key",1:"Step",2:"DJ",3:"Catch",4:"Pad",5:"Taiko",6:"Ring",7:"Slide"}
        mode_name = mode_map.get(r.get("mode",0), "?")
        img = await chart_card(
            cid=cid, title=r.get("title","?"), version=r.get("version","?"),
            artist=r.get("artist",""), creator=r.get("creator",""),
            sid=sid, mode=mode_name, length=str(r.get("length","")),
            like=str(r.get("like","")), cover_url=cover)
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"chart: {e}"); await bot.send(event, "获取失败")
