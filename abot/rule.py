from nonebot.rule import Rule
from nonebot.typing import T_State
from nonebot.adapters import Bot, Event
from nonebot.adapters.cqhttp import GroupRecallNoticeEvent

async def _group_notice_recall(bot: "Bot", event: "Event", state: T_State) -> bool:
    return isinstance(event, GroupRecallNoticeEvent)

GROUP_NOTICE_RECALL = Rule(_group_notice_recall)