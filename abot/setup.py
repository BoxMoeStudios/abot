from nonebot.plugin.export import Export

def export_plugin(export: Export, name: str, usage: str):
    setattr(export, 'name', name)
    setattr(export, 'usage', usage)