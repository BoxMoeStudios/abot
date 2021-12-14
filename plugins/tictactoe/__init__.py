from typing import Dict, List
from nonebot import CommandGroup, export
from nonebot.log import logger
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GROUP, GroupMessageEvent, MessageSegment, Message
from .chess import Chess
from abot.message import get_at
from abot.setup import export_plugin
from abot.store import StoreClient
import random

__plugin_name__ = '井字棋'
__plugin_usage__ = '''【井字棋】
创建对局: /#new
接受对局: /#ac
落子: /#go 坐标
退出: /#quit
'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

store = StoreClient()

class Game:
    def __init__(self):
        self.rooms: Dict[int, Chess] = {}
        self.players: Dict[int, List[int]] = {}
        self.invitees: Dict[int, int] = {}

    def create(self, gid: int, uin: int, invitee: int):
        if gid in self.rooms:
            raise ValueError('对局进行中，等下一局吧')
    
        self.rooms[gid] = Chess()
        self.players[gid] = [uin]

        if invitee:
            self.invitees[gid] = invitee

        logger.info(f'/# players: {self.players}, invitees: {self.invitees}')

    def destroy(self, gid: int, uin: int):
        c = self.rooms.get(gid)
        if c:
            if uin in self.players[gid]:
                del self.rooms[gid]
                del self.players[gid]
                if gid in self.invitees:
                    del self.invitees[gid]
                return
            raise ValueError('你不能终止别人的对局噢~')
        raise ValueError('当前无对局，发送 /#new 新建一个吧')
        

    def join(self, gid: int, uin: int):
        if gid not in self.rooms:
            raise ValueError('当前无对局，发送 /#new 新建一个吧')
        
        if len(self.players[gid]) >= 2:
            raise ValueError('人数已满，等下一局吧')

        if gid in self.invitees and uin != self.invitees[gid]:
            raise ValueError('对方没有邀请你呢，先看别人玩儿吧')

        if uin in self.players[gid]:
            raise ValueError('你已经在房间里了哦')

        self.players[gid].append(uin)
        random.shuffle(self.players[gid]) # 原地乱序
        logger.info(f'/# players: {self.players}, invitees: {self.invitees}')

    def player(self, gid: int) -> List[int]:
        return self.players.get(gid)

    def go(self, gid: int, uin: int, pos: str) -> int:
        if gid not in self.rooms:
            raise ValueError('当前无对局，发送 /#new 新建一个吧')

        players = self.players[gid]
        room = self.rooms[gid]

        if uin not in players:
            raise ValueError('你不在当前对局中，先看别人玩会儿吧')

        if room.turn() != players.index(uin):
            raise ValueError('还没到你的回合哦')

        try:
            self.rooms[gid].set(pos)
        except ValueError as ve:
            raise ve
        
        return self.rooms[gid].check()


    def graph(self, gid: int) -> Chess:
        return self.rooms.get(gid)
        


game = Game()

group = CommandGroup('#', permission=GROUP)
new = group.command('new', aliases={'#new'})
ac = group.command('ac', aliases={'#ac'})
go = group.command('go', aliases={'#go'})
quit = group.command('quit', aliases={'#quit'})

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

    

    

