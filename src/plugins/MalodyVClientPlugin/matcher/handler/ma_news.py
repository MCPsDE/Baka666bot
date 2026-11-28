"""ma news - 系统消息/新闻 + 推送"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.log import logger
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.push.info import get_system_info
from ...MalodyAPI.push.message import get_messages


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    try:
        result = await asyncio.to_thread(get_system_info, access_token=user["access_token"], uid=uid)
        news = result.get("news", [])
        banners = result.get("banner", [])
        lines = []
        if news or banners:
            lines.append("系统消息:")
            for n in news[:5]:
                title = n.get("title", "?")
                desc = n.get("desc", "")
                lines.append(f"  {title}")
                if desc:
                    lines.append(f"    {desc[:80]}")
        try:
            msgs = await asyncio.to_thread(get_messages, access_token=user["access_token"], uid=uid)
            mdata = msgs.get("data", [])
            if mdata:
                lines.append("推送消息:")
                for m in mdata[:5]:
                    lines.append(f"  [{m.get('type','?')}] {m.get('message','')[:80]}")
        except Exception:
            pass
        if not lines:
            await bot.send(event, "暂无消息")
        else:
            await bot.send(event, "\n".join(lines[:15]))
    except Exception as e:
        logger.error(f"获取消息失败: {e}")
        await bot.send(event, "获取失败")
