"""ma createsong - 创建歌曲"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.community.song.create import create_song


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    parts = args.strip().split(maxsplit=1)
    if len(parts) < 2:
        await bot.send(event, "用法: ma createsong <标题> <艺术家>")
        return
    title, artist = parts[0], parts[1]
    try:
        r = await asyncio.to_thread(create_song, access_token=user["access_token"], uid=uid, title=title, artist=artist)
        await bot.send(event, f"歌曲创建成功！SID: {r.get('sid','?')}")
    except Exception:
        await bot.send(event, "创建失败")
