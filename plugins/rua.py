from nonebot import on_command, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment
from PIL import Image, ImageOps
from io import BytesIO
from abot.setup import export_plugin
from abot.message import get_at
from abot.qq import aget_av


__plugin__name__ = '摸一摸'
__plugin_usage__ = '''【摸一摸】
/摸一摸 @谁
/rua @谁'''

export_plugin(export(), __plugin__name__, __plugin_usage__)

rua = on_command(__plugin__name__, aliases={'rua'})

@rua.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    to = get_at(event)

    # if abot has been ated
    if to == 0:
        await rua.finish('讨厌，不让你摸~', at_sender=True)

    try:
        av = await aget_av(to)
    except ValueError:
        await rua.finish('后端跑路了啦~', at_sender=True)

    gif = petpet(av)
    await rua.finish(MessageSegment.image(gif))


frame_spec = [
    (27, 31, 86, 90),
    (22, 36, 91, 90),
    (18, 41, 95, 90),
    (22, 41, 91, 91),
    (27, 28, 86, 91),
]

squish_factor = [
    (0, 0, 0, 0),
    (-7, 22, 8, 0),
    (-8, 30, 9, 6),
    (-3, 21, 5, 9),
    (0, 0, 0, 0),
]

squish_translation_factor = [0, 20, 34, 21, 0]

frames = [Image.open(f'assets/petpet/frame{i}.png') for i in range(len(frame_spec))]


def make_frame(av: Image, i: int, squish=0, flip=False) -> Image:
    spec = list(frame_spec[i])
    for j, s in enumerate(spec):
        spec[j] = int(s + squish_factor[i][j] * squish)
    hand = frames[i]
    if flip:
        av = ImageOps.mirror(av)

    av = av.resize((int((spec[2] - spec[0]) * 1.2), int((spec[3] - spec[1]) * 1.2)), Image.ANTIALIAS)
    gif_frame = Image.new('RGB', (112, 112), (255, 255, 255))
    gif_frame.paste(av, (spec[0], spec[1]))
    gif_frame.paste(hand, (0, int(squish * squish_translation_factor[i])), hand)
    return gif_frame


def petpet(im: Image, flip=False, squish=0, fps=30) -> BytesIO:
    frames = []
    for i in range(len(frame_spec)):
        frames.append(make_frame(im, i, squish, flip))
    frame: Image
    frame = frames[0]
    buf = BytesIO()
    frame.save(buf, format="GIF", append_images=frames,
                   save_all=True, duration=fps, loop=0)
    return buf