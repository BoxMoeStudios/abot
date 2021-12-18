from typing import List
from nonebot.adapters import Event
from httpx import AsyncClient
from PIL import Image
from io import BytesIO
from .browser import get_ua
import re


av_url = "https://q2.qlogo.cn/headimg_dl?dst_uin=%s&spec=100"

async def aget_av(uin: int) -> Image:
    headers = {'User-Agent': get_ua()}
    async with AsyncClient() as c:
        resp = await c.get(av_url % uin, headers=headers)
    if resp.status_code != 200:
        raise ValueError('failded to fetch qq avatar')
    return Image.open(BytesIO(resp.content))


def get_at(ev: Event) -> int:
    msg = str(ev.get_message())
    r = re.search(r'(?<=\[CQ:at,qq=).*(?=\])', msg)
    if not r:
        return 0
    return int(r.group(0))


def get_image(s: str, flash_only=True) -> str: 
    if s.find('CQ:image') == -1:
        return None
    
    if s[10:].find('type=flash') == -1 and flash_only:
        return None

    r = re.search(r'(?<=url=).*(?=\])', s)

    return r.group(0) if r else None


