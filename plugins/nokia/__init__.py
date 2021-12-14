from nonebot import on_command, export
from nonebot.adapters.cqhttp import Bot, Event, MessageSegment
from nonebot.typing import T_State
from abot.setup import export_plugin

from .nokia import generate_image

__plugin_name__ = '诺基亚表情包'
__plugin_usage__ = '''【诺基亚表情包】
/nokia 内容
/nka 内容
/诺基亚 内容
'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

nka = on_command("nokia", aliases={"nka", "诺基亚"})


@nka.handle()
async def _(bot: Bot, event: Event, state: T_State):
    msg = str(event.get_message())
    buf = generate_image(msg)
    await nka.finish(MessageSegment.image(buf))
