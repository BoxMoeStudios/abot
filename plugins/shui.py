from typing import Dict, List, Set
from nonebot import on_message, export, CommandGroup
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GROUP, GroupMessageEvent, MessageSegment
from threading import RLock
from abot.setup import export_plugin
from random import randint, choice
import os

text_path = 'assets/shui/text.txt'
image_dir = 'assets/shui/img'
text_list: List[str]
image_paths: List[str]

def load_prepared_messages():
    global text_list, image_paths
    with open(text_path, encoding='utf8') as f:
        text_list = f.read().split('\n')

    image_paths = []
    file_names = os.listdir(image_dir)
    for name in file_names:
        path = os.path.join(image_dir, name)
        if os.path.isfile(path):
            image_paths.append(path)


load_prepared_messages()

async def get_next_message(msg: str):
    if randint(0, 1) == 1:
        return choice(text_list)
    
    with open(choice(image_paths), 'rb') as f:
        return MessageSegment.image(f.read())

class Channel:
    def __init__(self, uin: int):
        self.cd = self.get_cd()
        self.uin = {1366723936, uin}
        self.lock = RLock()

    def check(self):
        if self.cd > 0:
            self.cd -= 1
            return False

        # 重置复读 CD
        self.lock.acquire()
        self.cd = self.get_cd()
        self.lock.release()
        return True

    @staticmethod
    def get_cd() -> int:
        return randint(20, 50)

    def has_permission(self, uin: int) -> bool:
        return uin in self.uin

shui = on_message(permission=GROUP, block=False, priority=2)

channels: Dict[int, Channel] = {
    826653699: Channel(1366723936)
}

@shui.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    if gid not in channels: 
        return

    msg = event.raw_message

    if channels[gid].check():
        await shui.finish(await get_next_message(msg))

__plugin_name__ = 'shui'
__plugin_usage__ = '''
/开始水群
/停止水群'''

group = CommandGroup(__plugin_name__, priority=1)
start = group.command('start', aliases={'开始水群'})
stop = group.command('stop', aliases={'停止水群'})

export_plugin(export(), __plugin_name__, __plugin_usage__)

@start.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    uin = event.user_id
    uname = event.sender.nickname
    if gid not in channels:
        channels[event.group_id] = Channel(uin)
        await start.finish(f'<{uname}>打开了水群模式')

@stop.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    uin = event.user_id
    uname = event.sender.nickname
    if gid in channels:
        if not channels[gid].has_permission(uin):
            await stop.finish('谁打开的谁自己关...')

        del channels[event.group_id]
        await stop.finish(f'<{uname}>关闭了水群模式。')
