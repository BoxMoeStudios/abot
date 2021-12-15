from nonebot import on_command, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment
from abot.setup import export_plugin
from typing import Literal
from PIL import ImageFont, Image, ImageDraw
from math import sqrt
from io import BytesIO
import re

def split_to_lines(s: str, size: int, font: ImageFont, max_width: float) -> str:
    lines = []
    w, j = 0, 0
    for i, c in enumerate(s):
        w += font.getsize(c)[0]
        if max_width - w < size:
            lines.append(s[j:i+1])
            j = i+1
            w = 0
    lines.append(s[j:])
    return lines


async def draw_text(
    text: str, 
    font: str, 
    font_size: int = 40,
    line_height: float = 1.5,
    max_width: int = 200,
    max_height: int = None,
    align: Literal['left', 'right', 'center'] = 'center',
    fill=(0, 0, 0, 255),
) -> Image:
    fix = 0.4
    if max_height:
        font_size = int(sqrt(fix*max_width*max_height/len(text)))

    font = ImageFont.truetype(font, font_size)
    _, h = font.getsize(text[0])
    h2 = h * line_height
    spacing = h2 - h
    lines = split_to_lines(text, font_size, font, max_width)
    max_height = int(max_height or len(lines) * h2)

    new = Image.new('RGBA', (max_width, max_height), (255, 255, 255))
    drawer = ImageDraw.Draw(new)
    drawer.text((0, 0), '\n'.join(lines), font=font, align=align, spacing=spacing, fill=fill)
    return new


model = Image.open('assets/fan/fan.jpg')

async def make_image(text: str) -> BytesIO:
    im = model.copy()
    offset = len(text)*15 if len(text) < 3 else 0
    ps = await draw_text(text, 'assets/fan/font.ttf', max_height=120)
    im.paste(ps, (150+offset, 50))
    buf = BytesIO()
    im.save(buf, format='PNG')
    return buf

__plugin__name__ = 'fan'
__plugin_usage__ = '''【狂粉表情包】
/fan 名字
/狂粉 名字'''

export_plugin(export(), __plugin__name__, __plugin_usage__)

fan = on_command(__plugin__name__)

@fan.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    text = event.get_plaintext()
    if len(text) > 10:
        await fan.finish('名字太长了啦', at_sender=True)

    # if not re.match(r'([\u4e00-\u9fa5]|[a-zA-Z0-9])', text):
    #     await fan.finish('')

    await fan.finish(MessageSegment.image(await make_image(text)))

