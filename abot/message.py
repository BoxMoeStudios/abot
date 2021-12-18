from PIL import Image
from nonebot.adapters import Event
import re

def get_at(ev: Event) -> int:
    msg = str(ev.get_message())
    r = re.search(r'(?<=\[CQ:at,qq=).*(?=\])', msg)
    if not r:
        return 0
    return int(r.group(0))


def get_image(ev: Event, flash_only=True) -> Image:
    pass