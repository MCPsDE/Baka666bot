from nonebot import on_command
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.params import CommandArg
from nonebot.adapters import Message

from .handler.login_handler import process_login

# 登录/绑定引导命令
login_cmd = on_command("login", aliases={"登录", "绑定"}, priority=10, block=True)


@login_cmd.handle()
async def login(bot: Bot, event: Event, args: Message = CommandArg()):
    await process_login(bot, event, args.extract_plain_text().strip())