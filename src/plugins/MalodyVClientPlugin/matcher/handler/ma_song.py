"""ma song - 歌曲信息 (含封面)"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event, MessageSegment
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.song.info import get_song_info
from ...render.components import simple_rows

async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user: await bot.send(event, BIND_GUIDE_TEXT); return
    sid = args.strip()
    if not sid or not sid.isdigit(): await bot.send(event, "用法: ma song <SID>"); return
    try:
        r = await asyncio.to_thread(get_song_info, access_token=user["access_token"], uid=uid, sid=sid)
        rows = [("标题", r.get("title","?")), ("艺术家", r.get("artist","?")),
                ("原标题", r.get("titleOrg","")), ("原艺术家", r.get("artistOrg","")),
                ("BPM", str(r.get("bpm",""))), ("长度", f"{r.get('length','')}s"),
                ("SID", sid), ("封面", r.get("cover","")[:40])]
        img = await simple_rows(f"歌曲 SID:{sid}", [(k,v) for k,v in rows if v])
        await bot.send(event, MessageSegment.image(img))
    except Exception as e:
        logger.error(f"song: {e}"); await bot.send(event, "获取失败")
