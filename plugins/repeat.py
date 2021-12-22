from typing import Dict, List, Set
from nonebot import on_message, export, CommandGroup
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GROUP, GroupMessageEvent, Message
from threading import RLock
from abot.setup import export_plugin
from abot.message import compare_messages
from random import randint

class Channel:
    def __init__(self, i: int):
        self.c: List[Message] = []
        self.i = i
        self.cd = 0
        self.lock = RLock()
        self.last: Message = None

    def add(self, s: Message):
        self.lock.acquire()
        self.c.append(s)
        if len(self.c) > self.i:
            self.c = self.c[1:]
        self.lock.release()

    def check(self):
        self.lock.acquire()
        s = self.c
        self.lock.release()

        n = len(s)
        if n < 2:
            return False

        if not compare_messages(self.last, s[n-1]):
            self.cd = 0

        if self.cd > 0:
            self.cd -= 1
            return False

        
        for i in range(0, n-1):
            if not compare_messages(s[i], s[i+1]):
                return False

        # 重置复读 CD
        self.lock.acquire()
        self.cd = randint(5, 15)
        self.lock.release()

        self.last = s.pop()
        return True

    def clear(self):
        self.lock.acquire()
        self.c.clear()
        self.lock.release()

repeat = on_message(permission=GROUP, block=False, priority=2)

channels: Dict[int, Channel] = {}

@repeat.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    if gid not in channels: 
        channels[gid] = Channel(2)

    msg = event.message
    channels[gid].add(msg)

    if channels[gid].check():
        channels[gid].clear()
        await repeat.finish(msg)

__plugin_name__ = 'repeat'
__plugin_usage__ = '''
/开始复读
/停止复读'''

group = CommandGroup(__plugin_name__, priority=1)
start = group.command('start', aliases={'开始复读'})
stop = group.command('stop', aliases={'停止复读'})

export_plugin(export(), __plugin_name__, __plugin_usage__)

@start.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    if gid not in channels:
        channels[event.group_id] = Channel(2)
    await start.finish('已开启复读，发送 "/停止复读" 可关闭复读模式')

@stop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    if gid in channels:
        del channels[event.group_id]
    
    await stop.finish('已关闭复读，发送 "/开始复读" 可再次打开复读模式')
