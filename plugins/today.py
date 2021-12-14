from nonebot import on_command, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment
from httpx import AsyncClient
from datetime import date
from random import choice
from abot.setup import export_plugin
import re

__plugin_name__ = 'today'
__plugin_usage__ = '''【历史上的今天】
/today
/今天'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

_url = 'https://baike.baidu.com/cms/home/eventsOnHistory/%s.json'

today = on_command('today', aliases={'今天', '历史上的今天'})

@today.handle()
async def _(bot: Bot):
    td = date.today()
    ev = await history(td)
    title = clean(ev["title"])
    share = ev.get('pic_share')
    reply = f'历史上的今天: {ev["year"]}年{td.month}月{td.day}日, {title}。点击下面链接查看详情'
    await today.send(reply, at_sender=True)
    await today.finish(MessageSegment.share(ev['link'], title, image=share))



async def history(today: date):
    month = format(today.month)
    day = format(today.day)
    async with AsyncClient() as c:
        r = await c.get(_url % month)

    if r.status_code != 200:
        return f'今天是 {today.strftime("%Y 年 %m 月%d 日")}'

    return choice(r.json()[month][f'{month}{day}'])

def format(i: int) -> str:
    return f'0{i}' if i < 10 else str(i)

def clean(s: str) -> str:
    return re.sub(r'<[^<]+?>', '', s).replace('\n', '').strip()
