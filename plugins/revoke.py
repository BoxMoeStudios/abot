from typing import Dict, List
from nonebot import on_notice, on_message, on_command, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupRecallNoticeEvent, GroupMessageEvent, GROUP, Message
from abot.rule import GROUP_NOTICE_RECALL
from abot.store import DefaultStore
from abot.setup import export_plugin
from abot.qq import get_image
from abot.browser import get_ua
from random import randint

class Channel:
    def __init__(self, n = 100):
        self.n = n
        self.queue: Dict[int, Message]= {}
        self.recall_list: List[int] = []

    async def add(self, mid: int, msg: Message):
        self.queue[mid] = msg
        if len(self.queue) > self.n:
            # persistent
            self.queue.clear()

    async def add_recall_id(self, mid: int):
        self.recall_list.append(mid)
        if len(self.recall_list) > self.n:
            # persistent?
            self.recall_list = self.recall_list[1:]

    async def last_recalled_message(self) -> Message:
        mid = await self.pop_last_recall_id()
        if mid not in self.queue:
            raise KeyError('failed to find the last recalled message')
        return self.queue[mid]

    async def pop_last_recall_id(self) -> int:
        return self.recall_list.pop()


channels: Dict[int, Channel] = {}

message = on_message(
    permission=GROUP, 
    block=False,
    priority=2
)

@message.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    if gid not in channels:
        channels[gid] = Channel()
    await channels[gid].add(event.message_id, event.message)


notice = on_notice(
    rule=GROUP_NOTICE_RECALL,
    block=False,
    priority=2
)

@notice.handle()
async def _(bot: Bot, event: GroupRecallNoticeEvent):
    gid = event.group_id
    if gid not in channels:
        channels[gid] = Channel()
     
    await channels[gid].add_recall_id(event.message_id)



__plugin_name__ = '反撤回'
__plugin_usage__ = '''【显示上条被撤回的消息】
命令: /反撤回 或 /fch
花费:  100 金币
'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

anti = on_command(__plugin_name__, aliases={'fch', '反撤回'})

__cost = 100

@anti.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    if gid not in channels:
        await anti.finish('当前还没有消息被撤回哦', at_sender=True)

    uin = event.user_id
    a = DefaultStore.get_coin(uin)
    if a < __cost:
        await anti.finish('你的金币数少于 100，不能使用该功能哦', at_sender=True)

    try:
        last_recalled = await channels[gid].last_recalled_message()
    except KeyError:
        await anti.finish('反撤回失败，被撤回的消息太久远啦~', at_sender=True)
    
    await anti.send(last_recalled)
    DefaultStore.decr_coin(uin, __cost)


fxl = on_command('反小丽')

@fxl.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uin = event.user_id
    n = randint(1, 10)
    DefaultStore.transfer_coin(uin, 1366723936, n)
    await fxl.finish(f'你赠送了 {n} 个金币给小丽', at_sender=True)