"""ma search - 搜索玩家"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.player.search import search_player


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return

    keyword = args.strip()
    if not keyword:
        await bot.send(event, "用法: ma search <关键词>")
        return

    try:
        result = await asyncio.to_thread(
            search_player, keyword=keyword, access_token=user["access_token"], uid=uid, limit=10
        )
        data = result.get("data", [])
        if not data:
            await bot.send(event, "未找到匹配的玩家")
            return
        lines = ["搜索结果:"]
        for i, p in enumerate(data[:10], 1):
            lines.append(f"{i}. {p.get('username','?')} (UID:{p.get('uid','?')})")
        await bot.send(event, "\n".join(lines))
    except Exception as e:
        logger.error(f"搜索失败: {e}")
        await bot.send(event, "搜索失败")
