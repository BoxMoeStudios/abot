from nonebot import on_command
from nonebot.permission import SUPERUSER
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import MessageSegment, GroupMessageEvent
from nonebot.typing import T_State

admin = on_command('admin', permission=SUPERUSER)


@admin.handle()
async def _(bot: Bot, event: Event):
    await admin.send(f'超管<{event.get_user_id()}>已进入')


@admin.got('op', '请输入操作')
async def _(bot: Bot, event: Event, state: T_State):
    op = state["op"]
    if op == 'quit':
        await admin.finish(f'超管<{event.get_user_id()}>已退出')

    await admin.send(f'获取操作: {op}')
    del state['op']


test = on_command('test', permission=SUPERUSER)

@test.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    await test.finish()