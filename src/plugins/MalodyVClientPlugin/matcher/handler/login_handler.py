from nonebot.adapters.onebot.v11 import Bot, Event

from ...MalodyAPI.core import SITE_BASE
from .user_utils import BIND_GUIDE_TEXT, get_user_creds

pending_logins = {}


async def process_login(bot: Bot, event: Event, args: str):
    qq = str(event.get_user_id())
    uid, user = await get_user_creds(qq)
    if user:
        await bot.send(
            event,
            f"当前 QQ({qq}) 已绑定 Malody 账号：{user.get('username', uid)} (UID: {uid})。\n"
            f"如需更换绑定 QQ，请前往 {SITE_BASE} 个人主页修改。",
        )
        return
    await bot.send(event, BIND_GUIDE_TEXT)