from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot

ping = on_command('ping', rule=to_me())

@ping.handle()
async def _(bot: Bot):
    await ping.finish('pong')

