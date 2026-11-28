"""ma logout - 云端绑定解绑指引"""
from nonebot.adapters.onebot.v11 import Bot, Event
from ...MalodyAPI.core import SITE_BASE


async def handle(bot: Bot, event: Event, args: str):
    await bot.send(event, f"当前已使用 {SITE_BASE} 云端绑定，如需解除 QQ 关联请前往 {SITE_BASE} 个人主页操作。")