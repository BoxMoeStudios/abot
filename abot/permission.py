from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GroupMessageEvent
from nonebot.permission import Permission

async def _group_no_anonymous(bot: "Bot", event: "Event") -> bool:
    return isinstance(event, GroupMessageEvent) and not event.anonymous

GROUP_NO_ANONYMOUS = Permission(_group_no_anonymous)