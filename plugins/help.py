from typing import Dict, List
from nonebot import on_command, get_loaded_plugins
from nonebot.adapters import Bot, Event

plugins: Dict[str, dict] = {}

def load_plugin_info():
    for plugin in get_loaded_plugins():
        name = plugin.export.get('name')
        if name:
            plugins[name] = plugin.export
    

help = on_command('help', aliases={'帮助', '菜单', 'menu'})

@help.handle()
async def _(bot: Bot, event: Event, state: dict):
    if not plugins:
        load_plugin_info()

    arg = event.get_plaintext().strip()
    if arg:
        state['name'] = arg
        return

    names = ', '.join(plugins.keys())

    print(names)

    await help.send('现在支持的功能有: '+ names)
    await help.finish('发送 "/help 功能" 可查看功能的具体使用方法。')

@help.got('name', prompt='你要查看那个功能的使用方法呢？')
async def _(bot: Bot, event: Event, state: dict):
    name = state.get('name')
    if name:
        usage = plugins[name].get('usage')
        await help.finish(usage)

# 1️⃣2️⃣3️⃣4️⃣5️⃣6️⃣7️⃣8️⃣9️⃣🔟