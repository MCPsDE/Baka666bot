"""ma delaccount - 注销账号（二次确认）"""
import asyncio
from nonebot.adapters.onebot.v11 import Bot, Event
from .user_utils import BIND_GUIDE_TEXT, get_user_creds
from ...MalodyAPI.account.deletion import delete_account

_CONFIRM = {}


async def handle(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if not user:
        await bot.send(event, BIND_GUIDE_TEXT)
        return
    if args.strip() == "confirm":
        try:
            await asyncio.to_thread(delete_account, access_token=user["access_token"], uid=uid)
            await bot.send(event, "账号已注销")
        except Exception:
            await bot.send(event, "注销失败")
        return
    await bot.send(event, "⚠️ 此操作不可撤销！输入 ma delaccount confirm 确认注销")