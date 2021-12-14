from redis import Redis
from datetime import datetime, timedelta

class StoreClient:
    c = Redis()

    def get_coin(cls, uin: int) -> int:
        return cls.geti(f'bot:coin:{uin}')

    def incr_coin(cls, uin: int, a: int) -> int:
        return cls.incr(f'bot:coin:{uin}', a)

    def transfer_coin(cls, frm: int, to: int, a: int) -> list:
        cmds = None
        with cls.c.pipeline() as pipe:
            pipe.incrby(f'bot:coin:{to}', a)
            pipe.decrby(f'bot:coin:{frm}', a)
            cmd = pipe.execute()
        return cmd

    def decr_coin(cls, uin: int, a: int) -> int:
        return cls.decr(f'bot:coin:{uin}', a)

    def incr(cls, key: str, a: int) -> int:
        return cls.c.incrby(key, a)

    def decr(cls, key: str, a: int) -> int:
        return cls.c.decrby(key, a)

    def geti(cls, key: str) -> int:
        b = cls.c.get(key)
        return int(b) if b else 0

    def seti(cls, key: str, value: int, ex: int) -> int:
        return cls.c.set(key, value, ex=ex)

def seconds_till_tomorrow() -> int:
    now = datetime.now()
    today = datetime(now.year, now.month, now.day, 0, 0, 0)
    tomorrow = today + timedelta(days=1)
    return (tomorrow - now).seconds

DefaultStore = StoreClient()