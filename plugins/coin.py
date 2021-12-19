from nonebot import CommandGroup, export
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import MessageSegment, GroupMessageEvent, GROUP_ADMIN
from abot.setup import export_plugin
from abot.store import StoreClient, seconds_till_tomorrow
from abot.message import get_at
from abot.permission import GROUP_NO_ANONYMOUS
from random import randint

store = StoreClient()

__plugin__name__ = '$'
__plugin_usage__ = '''【金币】
查看金币: /$me
获取金币: /$get
赠送金币: /$send 数量 @谁'''

export_plugin(export(), __plugin__name__, __plugin_usage__)

coin = CommandGroup(__plugin__name__, permission=GROUP_NO_ANONYMOUS)
me = coin.command('me', aliases={'$me', '$ me'})
send = coin.command('send', aliases={'$send', '$ send'})
get = coin.command('get', aliases={'$get', '$ get'})

@me.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    a = store.get_coin(event.user_id)
    await me.finish(f'你有 {a} 个金币', at_sender=True)


@send.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    to = get_at(event)
    uin = event.user_id

    cost = event.get_plaintext().strip()
    cost = int(cost) if cost.isdigit() else 0

    if cost:
        if to == 0:
            await send.finish('谢谢老板~', at_sender=True)

        if to == uin:
            await send.finish('你赠送自己干嘛？', at_sender=True)

        a = store.get_coin(uin)
        if a >= cost:
            store.transfer_coin(uin, to, cost)
            at_sender = False
            reply = MessageSegment.at(uin) + f' 赠送了 {cost} 个金币给 ' + MessageSegment.at(to)
        else:
            at_sender = True
            reply = f'赠送失败，你只有 {a} 个金币。'
        
        await send.finish(reply, at_sender=at_sender)


@get.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    uin = event.user_id

    a = store.geti(f'bot:coin:today:{uin}')
    if a:
        await get.finish('今天已经领过了哦，明天再来吧~', at_sender=True)
    
    a = randint(20, 100)
    store.incr_coin(uin, a)
    store.seti(f'bot:coin:today:{uin}', a, seconds_till_tomorrow())

    await get.finish(f'你领取了 {a} 个金币', at_sender=True)
    
