from nonebot import on_command, export
from nonebot.log import logger
from nonebot.adapters.cqhttp import MessageEvent, MessageSegment
from nonebot.adapters import Bot
from PIL import Image
from httpx import AsyncClient
from io import BytesIO
from abot.setup import export_plugin

__plugin_name__ = '灰头像'
__plugin_usage__ = '''【获取灰头像】
/grey
/gray
/灰头像'''

export_plugin(export(), __plugin_name__, __plugin_usage__)


_url = 'https://q2.qlogo.cn/headimg_dl?dst_uin=%s&spec=100'

_headers = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
    'Host': 'q1.qlogo.cn',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.55 Safari/537.36',
    # 'Upgrade-Insecure-Requests': '1',
    # 'Accept-Encoding': 'gzip, deflate',
    # 'Accept-Language': 'en,zh-CN;q=0.9,zh;q=0.8'
}

async def fetch_and_convert(qq: int):
    async with AsyncClient() as c:
        r = await c.get(_url % qq, headers=_headers)
    if r.status_code != 200:
        raise ValueError(f'fetch {r.status_code}')
    
    im = Image.open(BytesIO(r.content)).convert('L')
    buf = BytesIO()
    im.save(buf, format='JPEG')
    return buf

grey = on_command('grey', aliases={'gray', '灰头像'})


@grey.handle()
async def _(bot: Bot, event: MessageEvent):
    uin = event.user_id
    reply: str or MessageSegment

    try:
        buf = await fetch_and_convert(uin)
        reply = MessageSegment.image(buf)
    except ValueError as e:
        reply = '后端跑路了啦～'
        logger.error(e)
    
    await grey.finish(reply, at_sender=True)

