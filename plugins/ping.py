from nonebot import on_command, export
from nonebot.adapters import Bot
from abot.setup import export_plugin


__plugin__name__ = 'ping'
__plugin_usage__ = '''【查看机器人是否在线】
发送: /ping'''

export_plugin(export(), __plugin__name__, __plugin_usage__)

ping = on_command(__plugin__name__)

@ping.handle()
async def _(bot: Bot):
    await ping.finish('pong')

