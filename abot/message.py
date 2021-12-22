from nonebot.adapters import Event
from nonebot.adapters.cqhttp import Message
import re

def get_at(ev: Event) -> int:
    msg = str(ev.get_message())
    r = re.search(r'(?<=\[CQ:at,qq=).*(?=\])', msg)
    if not r:
        return 0
    return int(r.group(0))


def compare_messages(a: Message, b: Message) -> bool:
    if not a or not b:
        return False

    for s, t in zip(a, b):
        if s.type != t.type:
            return False

        if s.type == 'image':
            if t.type != 'image':
                return False

            return s.image == t.image
        
        if str(s) != str(t):
            return False

    return True