from typing import Union
from nonebot import on_command
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import PrivateMessageEvent, PRIVATE
from abot.store import StoreClient

store = StoreClient()

loss = on_command('loss', permission=PRIVATE)

__codes = { 'u1s1' }
__coin = 500

@loss.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    code = event.get_plaintext()
    if code not in __codes:
        await loss.finish('无效补偿码')

    uin = event.user_id
    key = f'bot:loss:{code}'
    if store.client().sismember(key, uin):
        await loss.finish('你已经领过补偿了哦~')

    with store.client().pipeline() as pipe:
        pipe.incrby(f'bot:coin:{uin}', __coin)
        pipe.sadd(key, uin)
        res = pipe.execute()

    await loss.finish(f'你领取了 {__coin} 个金币作为补偿')
