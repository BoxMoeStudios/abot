from typing import Dict, Union
from nonebot import export, require, get_bot, CommandGroup
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, Message, Bot as CQHTTPBot, message
from abot.setup import export_plugin
from abot.permission import GROUP_NO_ANONYMOUS
from abot.store import DefaultStore
from dataclasses import dataclass
from uuid import uuid4


@dataclass
class Task:
    uin: int
    gid: int
    content: Message = None
    interval: int = None

    def __str__(self) -> str:
        return f"{self.uin} {self.gid} {self.interval} {self.content}"

__tasks: Dict[str, Task] = {}

scheduler = require('nonebot_plugin_apscheduler').scheduler

__plugin_name__ = '定时消息'
__plugin_usage__ = '''【自定义定时消息】
指令:
/task add
/task rm 消息id
花费: 
10 金币
提示:
定时消息创建成功后会返回其“消息id”用于删除'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

task = CommandGroup('task', permission=GROUP_NO_ANONYMOUS)
add = task.command('add', aliases={'添加定时消息'})
remove = task.command('rm', aliases={'删除定时消息'})

__cost = 10

@add.handle()
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    gid = event.group_id
    uin = event.user_id
    a = DefaultStore.get_coin(uin)
    if a < __cost:
        await add.finish('你的金币数不足 10 个', at_sender=True)

    task_id = uuid4().__str__()[:8]
    state['task_id'] = task_id
    __tasks[task_id] = Task(uin, gid)

__content_prompt = '请输入定时消息内容'
@add.got('content', prompt=__content_prompt)
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    content = state['content']
    if not content:
        await add.reject(__content_prompt, at_sender=True)

    task_id = state['task_id']
    __tasks[task_id].content = event.message


__max_interval = 2880
__min_interval = 10
__interval_prompt = '请输入定时消息间隔（分钟）'
@add.got('interval', prompt=__interval_prompt)
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    interval: str = state['interval']
    if not interval or not interval.isdigit():
        await add.reject(__interval_prompt, at_sender=True)
    minites = int(interval)
    if minites < __min_interval or minites > __max_interval:
        await add.reject(f"{__min_interval} < 消息间隔 < {__max_interval}, 重新输入", at_sender=True)
    task_id = state['task_id']
    __tasks[task_id].interval = minites


__confirm_prompt = '确认: OK, 取消: NO'
@add.got('confirm', prompt=__confirm_prompt)
async def _(bot: Bot, event: GroupMessageEvent, state: dict):
    confirm = state['confirm']
    if confirm not in ('OK', 'NO', 'ok', 'no'):
        await add.reject(__confirm_prompt, at_sender=True)
    if confirm in ('NO', 'no'):
        await add.finish('已取消定时消息编辑', at_sender=True)
    
    task_id = state['task_id']
    task = __tasks[task_id]
    scheduler.add_job(make_task, 'interval', minutes=task.interval, args=[task])

    DefaultStore.decr_coin(task.uin, __cost)
    await add.finish(f'添加成功! 发送 "/task rm {task_id}" 可删除该定时消息', at_sender=True)

async def make_task(*arg):
    task: Task = arg[0]
    bot: CQHTTPBot = get_bot()
    await bot.send_group_msg(group_id=task.gid, message=task.content)
    

@remove.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    task_id = event.get_plaintext()
    uin = event.user_id
    gid = event.group_id
    task = __tasks.get(task_id)
    if task:
        if task.uin == uin and task.gid == gid:
            del __tasks[task_id]
            await remove.finish(f'已删除定时消息 {task_id}', at_sender=True)
        await remove.finish('谁设置的谁删掉~', at_sender=True)
