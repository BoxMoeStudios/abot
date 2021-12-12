from nonebot import on_command
from nonebot.rule import to_me
from nonebot.adapters import Bot

translate = on_command('fy', aliases={'翻译'}, rule=to_me())

@translate.handle()
async def _(bot: Bot):
    await translate.finish('pong')