"""ma chartonline - 在线谱面信息"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.chart.online import get_chart_online


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    hash_ = args.strip()
    if not hash_:
        await bot.send(event, "用法: ma chartonline <hash>")
        return
    try:
        r = await asyncio.to_thread(get_chart_online, access_token=user["access_token"], uid=uid, hash_=hash_)
        song = r.get("song", {})
        chart = r.get("chart", {})
        if not song:
            await bot.send(event, "未找到该 hash 对应的谱面")
            return
        lines = [
            f"在线谱面: hash={hash_}",
            f"  歌曲: {song.get('title','?')} / {song.get('artist','?')}",
            f"  BPM:{song.get('bpm',0)} 长度:{song.get('length',0)}s",
            f"  难度: {chart.get('version','?')} Lv.{chart.get('level','?')}",
        ]
        await bot.send(event, "\n".join(lines))
    except Exception as e:
        logger.error(f"获取在线谱面失败: {e}")
        await bot.send(event, "获取失败")
