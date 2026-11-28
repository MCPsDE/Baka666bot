"""ma renew - 刷新云端会话令牌"""
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq, force_refresh=True)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    await bot.send(event, f"已从云端刷新令牌：{user.get('username', uid)} (UID: {uid})")