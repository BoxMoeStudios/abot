from nonebot import on_command
from nonebot.rule import to_me
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event

weather = on_command('天气', aliases={'tq'}, rule=to_me())

@weather.handle()
async def receive(bot: Bot, event: Event, state: T_State):
    pass

@weather.got('city', prompt='你想要查询哪个城市的天气呢？')
async def _(bot: Bot, event: Event, state: T_State):
    city = state['city']
    await weather.finish(await fetch_weather(city))


async def fetch_weather(city: str):
    return f'{city} 的天气是...'