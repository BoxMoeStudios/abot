from nonebot import on_command, export
from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from nonebot.adapters import Bot
from PIL import Image
from httpx import AsyncClient
from io import BytesIO
from abot.setup import export_plugin
from abot.qq import aget_av

__plugin_name__ = 'grey'
__plugin_usage__ = '''【获取灰头像】
/grey
/gray
/灰头像'''

export_plugin(export(), __plugin_name__, __plugin_usage__)


async def fetch_and_convert(qq: int):
    im = (await aget_av(qq)).convert('L')
    buf = BytesIO()
    im.save(buf, format='JPEG')
    return buf


grey = on_command('grey', aliases={'gray', '灰头像'})


@grey.handle()
async def _(bot: Bot, event: MessageEvent):
    
    try:
        buf = await fetch_and_convert(event.user_id)
        reply = MessageSegment.image(buf)
    except ValueError:
        reply = '后端跑路了啦～'
    
    await grey.finish(reply, at_sender=True)

