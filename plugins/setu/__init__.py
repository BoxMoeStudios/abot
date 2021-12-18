from nonebot import on_command, on_notice
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import MessageSegment, NoticeEvent
from PIL import Image
from io import BytesIO

setu = on_command('setu', aliases={'涩图', '色图', '来点色图', '来点涩图'})
nosese = Image.open('assets/anti/nosese.jpg')
nosese_buf = BytesIO()
nosese.save(nosese_buf, format='JPEG')

@setu.handle()
async def _(bot: Bot):
    await setu.finish(MessageSegment.image(nosese_buf), at_sender=True)




