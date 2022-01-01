from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment
from abot.permission import GROUP_NO_ANONYMOUS
from abot.store import StoreClient
from random import choice

store = StoreClient()

loss = on_command('2022', permission=GROUP_NO_ANONYMOUS)

__coin = 2022

__wishes = {
    241050791: ['祝你上岸噢!', '你一定能上岸!', '你终硕!'],
    826653699: ['祝你考试通过!', '你是最棒的!', '祝你考 100 分!']
}

@loss.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    code = '2022'

    if str(event.message) != '[CQ:face,id=120]':
        return

    uin = event.user_id
    key = f'bot:bonus:{code}'
    if store.client().sismember(key, uin):
        await loss.finish('你已经领过 2022 新年礼包啦~', at_sender=True)

    with store.client().pipeline() as pipe:
        pipe.incrby(f'bot:coin:{uin}', __coin)
        pipe.sadd(key, uin)
        pipe.execute()

    gid = event.group_id
    wish = choice(__wishes[gid]) if gid in __wishes else ''

    await loss.finish(f'你领取了 2022 新年礼包: {__coin} 个金币, {wish}', at_sender=True)