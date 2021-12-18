from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GroupMessageEvent, NoticeEvent
from nonebot.permission import Permission

async def _group_no_anonymous(bot: "Bot", event: "Event") -> bool:
    return isinstance(event, GroupMessageEvent) and not event.anonymous

async def _group_notice_recall(bot: "Bot", event: "Event") -> bool:
    return isinstance(event, NoticeEvent) and event.notice_type == 'group_recall'

GROUP_NO_ANONYMOUS = Permission(_group_no_anonymous)
GROUP_NOTICE_RECALL = Permission(_group_notice_recall)