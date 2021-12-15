from nonebot import CommandGroup, export
from nonebot.log import logger
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment
from .chess import Game
from abot.message import get_at
from abot.setup import export_plugin
from abot.store import StoreClient
from abot.permission import GROUP_NO_ANONYMOUS

__plugin_name__ = '井字棋'
__plugin_usage__ = '''【井字棋】
创建对局: /#new
接受对局: /#ac
落子: /#go 坐标
退出: /#quit
'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

store = StoreClient()
game = Game()

group = CommandGroup('#', permission=GROUP_NO_ANONYMOUS)
new = group.command('new', aliases={'#new', '# new'})
ac = group.command('ac', aliases={'#ac', '# ac'})
go = group.command('go', aliases={'#go', '# go'})
quit = group.command('quit', aliases={'#quit', '# quit'})

@new.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    uin = event.user_id
    uname = event.sender.card or event.sender.nickname
    invitee = get_at(event)

    if uin == invitee:
        await new.finish('自己打自己可还行~', at_sender=True)

    a = store.get_coin(uin)
    if a < 0:
        await new.finish('你的金币数不足 0 个，不能开局', at_sender=True)
    
    try:
        game.create(gid, uin, invitee)
    except ValueError as e:
        await new.finish(str(e), at_sender=True)

    logger.info(f'/#new {uname}<{uin}> {invitee}')

    if invitee:
        await new.finish(f'<{uname}>向你发起井字棋对决，发送 /#ac 接受对局' + MessageSegment.at(invitee))
    await new.finish(f'<{uname}>发起井字棋对局，发送 /#ac 接受对局')
    

    
@quit.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    uin = event.user_id
    uname = event.sender.card or event.sender.nickname

    n = len(game.player(gid))

    try:
        game.destroy(gid, uin)
    except ValueError as e:
        logger.error(f'#({gid}): {e}')

    if n >= 2:
        store.decr_coin(uin, 5)
        await quit.finish(f'<{uname}>认输了，金币-5')

    await quit.finish(f'<{uname}>结束了对局')

    


@ac.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    uin = event.user_id
    uname = event.sender.card or event.sender.nickname
    logger.info(f'/#ac {uname}<{uin}>')
    try:
        game.join(gid, uin)
    except ValueError as e:
        await ac.finish(str(e), at_sender=True)
       
    p1, _ = game.player(gid)
    await ac.finish(
        '<{}>已加入对局\n先手是'.format(uname) + \
        MessageSegment.at(p1) + \
        '\n\n落子: /#go 坐标\n' + \
        '退出: /#quit\n\n' + \
        game.graph(gid).__str__()
    )



@go.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    gid = event.group_id
    uin = event.user_id
    pos = event.get_plaintext().strip()

    try:
        check = game.go(gid, uin, pos)
    except ValueError as ve:
        await go.finish(f'{ve}', at_sender=True)

    graph = game.graph(gid)
    await go.send(f'{graph}')

    p1, p2 = game.player(gid)
    if check == 3 or check == -3:
        winner = p1 if check == -3 else p2
        loser = p1 if winner == p2 else p2
        await go.send(
            '对局结束！' + \
            MessageSegment.at(loser) + ' 输了 10 个金币给 ' + \
            MessageSegment.at(winner)
        )
        store.transfer_coin(loser, winner, 10)
        game.destroy(gid, p1)

    if check == 9:
        await go.send(f'平局！')
        game.destroy(gid, p1)

    

    

