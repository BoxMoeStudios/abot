from nonebot.adapters import Event
import re

def get_at(ev: Event) -> int:
    msg = str(ev.get_message())
    r = re.search(r'(?<=\[CQ:at,qq=).*(?=\])', msg)
    if not r:
        return 0
    return int(r.group(0))