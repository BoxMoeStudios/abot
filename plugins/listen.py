from typing import Dict, List
from PIL import Image
from nonebot import on_message
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GROUP, GroupMessageEvent, Message
from abot.qq import get_image
from abot.browser import get_ua
from httpx import AsyncClient
from io import BytesIO


class Channel:
    def __init__(self, flash_limit=10, message_limit=100):
        self.flash_limit = flash_limit
        self.message_limit = message_limit
        self.flashes: List[str] = []

    def add_flash(self, url: str):
        self.flashes.append(url)
        if len(self.flashes) > self.flash_limit:
            # todo: persistent?
            self.flashes = self.flashes[1:]

    def last_flash(self) -> str:
        return self.flashes.pop() if self.flashes else None

class Cache:
    channels: Dict[int, Channel] = {}

    @classmethod
    async def save_flash_image(cls, ev: GroupMessageEvent):
        gid = ev.group_id
        url = get_image(str(ev.message))
        if not url:
            return
        
        if gid not in cls.channels:
            cls.channels[gid] = Channel()

        cls.channels[gid].add_flash(url)

    @classmethod
    async def last_flash_image(cls, ev: GroupMessageEvent) -> Image:
        gid = ev.group_id
        if gid not in cls.channels:
            return None
        
        url = cls.channels[gid].last_flash()
        if not url:
            return None

        async with AsyncClient() as c:
            headers = {'User-Agent': get_ua()}
            resp = await c.get(url, headers=headers)

        if resp.status_code != 200:
            return None
        
        return Image.open(BytesIO(resp.content))


cache = Cache()

async def get_last_flash_image(ev: GroupMessageEvent) -> Image:
    im = await cache.last_flash_image(ev)
    if not im:
        raise ValueError('恢复失败，上一张闪照太久远啦')
    return im

listen = on_message(
    permission=GROUP, 
    block=False,
    priority=2
)

@listen.handle()
async def flash(bot: Bot, event: GroupMessageEvent):
    await cache.save_flash_image(event)


    
