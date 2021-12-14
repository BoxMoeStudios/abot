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