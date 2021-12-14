from nonebot import on_command, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment
from PIL import Image, ImageDraw
from io import BytesIO
from abot.setup import export_plugin
from abot.message import get_at
from abot.qq import aget_av


__plugin__name__ = '亲亲'
__plugin_usage__ = '''【亲亲】
/亲亲 @谁
/kiss @谁'''

export_plugin(export(), __plugin__name__, __plugin_usage__)

rua = on_command(__plugin__name__, aliases={'kiss'})

from_x = [92, 135, 84, 80, 155, 60, 50, 98, 35, 38, 70, 84, 75]
from_y = [64, 40, 105, 110, 82, 96, 80, 55, 65, 100, 80, 65, 65]
to_x = [58, 62, 42, 50, 56, 18, 28, 54, 46, 60, 35, 20, 40]
to_y = [90, 95, 100, 100, 100, 120, 110, 100, 100, 100, 115, 120, 96]


frames = [Image.open(f'assets/kiss/{i+1}.png') for i in range(len(from_x))]

async def make_frame(operator, target, i) -> Image:
    frame = frames[i]
    gif_frame = Image.new("RGB", (200, 200), (255, 255, 255))
    gif_frame.paste(frame, (0, 0))
    gif_frame.paste(target, (to_x[i - 1], to_y[i - 1]), target)
    gif_frame.paste(operator, (from_x[i - 1], from_y[i - 1]), operator)
    return gif_frame


async def kiss(frm: Image, to: Image, fps=25) -> BytesIO:
    frm = frm.resize((40, 40), Image.ANTIALIAS)
    size = frm.size
    r2 = min(size[0], size[1])
    circle = Image.new("L", (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = Image.new("L", (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    frm.putalpha(alpha)

    to = to.resize((50, 50), Image.ANTIALIAS)
    size = to.size
    r2 = min(size[0], size[1])
    circle = Image.new("L", (r2, r2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, r2, r2), fill=255)
    alpha = Image.new("L", (r2, r2), 255)
    alpha.paste(circle, (0, 0))
    to.putalpha(alpha)

    gif_frames = []
    for i in range(len(from_x)):
        gif_frames.append(await make_frame(frm, to, i))

    buf = BytesIO()
    frame = gif_frames[0]
    frame.save(buf, format="GIF", append_images=gif_frames,
                   save_all=True, duration=fps, loop=0)
    return buf

@rua.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    to = get_at(event)
    uin = event.user_id

    # if abot has been ated
    if to == 0:
        await rua.finish('讨厌，不让你亲~', at_sender=True)

    try:
        frm_im = await aget_av(uin)
        to_im = await aget_av(to)
    except ValueError:
        await rua.finish('后端跑路了啦~', at_sender=True)

    gif = await kiss(frm_im, to_im)
    await rua.finish(MessageSegment.image(gif))
