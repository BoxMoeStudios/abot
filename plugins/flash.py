from nonebot import on_command, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment
from .listen import get_last_flash_image
from abot.store import DefaultStore
from abot.setup import export_plugin
from io import BytesIO


__plugin_name__ = '反闪照'
__plugin_usage__ = '''【显示上一张闪照】
命令: /反闪照 或 /fsz
花费: 200 金币
'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

__cost = 200

block_list = { 826653699 }

flash = on_command(__plugin_name__, aliases={'fsz'})

@flash.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    if event.group_id in block_list:
        await flash.finish('该群已关闭反闪照功能', at_sender=True)

    uin = event.user_id
    a = DefaultStore.get_coin(uin)
    if a < __cost:
        await flash.finish(f'你的金币数小于 {__cost}, 不能使用该功能')

    try:
        im = await get_last_flash_image(event)
    except ValueError as e:
        await flash.finish(str(e))

    buf = BytesIO()
    im.save(buf, format='PNG')

    await flash.send(MessageSegment.image(buf))
    DefaultStore.decr_coin(uin, __cost)
