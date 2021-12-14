from nonebot.log import logger
from typing import List, Dict
import random
import re


class Chess:
    _indices = {
        'A': 1,
        'a': 1,
        'B': 2,
        'b': 2,
        'C': 3,
        'c': 3
    }

    _indices_y = _indices.keys()

    def __init__(self):
        self.players = []
        self.grid = [[0 for _ in range(3)] for _ in range(3)]
        self.chars = ('X', '  ', 'O')
        self.steps = 0

    def set(self, pos: str):
        r = re.search(r'\d\w', pos)
        if not r:
            raise ValueError('无效落子位置')

        pos = r.group(0)
        if pos[1] not in self._indices_y:
            raise ValueError('无效落子位置')
            
        x = int(pos[0])
        y = self._indices[pos[1]]

        if x < 1 or x > 3 or y < 1 or y > 3:
            raise ValueError('无效落子位置')

        if self.grid[x-1][y-1] != 0:
            raise ValueError('无效落子位置')

        self._set(x, y)

    def _set(self, x: int, y: int):
        self.grid[x-1][y-1] = -1 if self.next() == 1 else 1

    def next(self) -> int:
        self.steps += 1
        return self.turn()

    def turn(self) -> int:
        return self.steps%2

    def check(self) -> int:
        '''
        returns
        3:  O 胜
        -3: X 胜
        9:  平局
        -9: 继续
        '''
        m = self.grid
        # check rows
        for row in m:
            s = sum(row)
            if s == -3 or s == 3:
                return s

        # check colums
        for i in range(3):
            s = m[0][i] + m[1][i] + m[2][i]
            if s == -3 or s == 3:
                return s

        # check crosses
        s = m[0][0] + m[1][1] + m[2][2]
        if s == -3 or s == 3:
            return s
        s = m[0][2] + m[1][1] + m[2][0]
        if s == -3 or s == 3:
            return s

        return 9 if self.steps >= 9 else -9
        
    def __str__(self):
        s = '   A B C\n'
        for i, row in enumerate(self.grid):
            s += f'{i+1} '
            s += ' '.join(self.chars[j+1] for j in row)
            s += '\n'
        return s[:-1]


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
        
