from nonebot import on_command, export, require, get_bot
from nonebot.log import logger
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment, Message, Bot as CQHTTPBot
from abot.setup import export_plugin
from .leetcode import Cache


__plugin_name__ = 'leetcode'
__plugin__usage__ = '''【力扣每日一题】
/leetcode
/力扣
'''

export_plugin(export(), __plugin_name__, __plugin__usage__)

cache = Cache()

lc = on_command(__plugin_name__, aliases={'力扣'})

@lc.handle()
async def _(bot: Bot, event: GroupMessageEvent):
    try:
        question = await cache.get_today_question()
    except Exception as e:
        logger.error(str(e))
        await lc.finish('获取题目失败~ 可能后端跑路啦~')

    msg = Message()
    for el in question.split('\n'):
        msg.append(MessageSegment.text(el+'\n'))
    msg.append(MessageSegment.text('题目来源: 力扣每日一题'))

    await lc.finish(msg)




scheduler = require('nonebot_plugin_apscheduler').scheduler

@scheduler.scheduled_job('cron', hour=12, minute=0)
@scheduler.scheduled_job('cron', hour=18, minute=0)
@scheduler.scheduled_job('cron', hour=8, minute=0)
async def _():
    bot: CQHTTPBot = get_bot()

    try:
        question = await cache.get_today_question()
    except Exception as e:
        logger.error(str(e))
        return

    msg = Message()
    for el in question.split('\n'):
        msg.append(MessageSegment.text(el+'\n'))
    msg.append(MessageSegment.text('题目来源: 力扣每日一题'))

    groups = [g['group_id'] for g in await bot.get_group_list()]
    for gid in groups:
        if gid in cache.blacklist:
            continue
        await bot.send_msg(message_type='group', group_id=gid, message=msg)


__we_groups = [826653699]


@scheduler.scheduled_job('cron', hour=13, minute=30)
@scheduler.scheduled_job('cron', hour=8, minute=0)
async def _():
    bot: CQHTTPBot = get_bot()

    msg = Message()
    msg.append(MessageSegment.text('We 重邮打卡啦乖乖们 '))
    msg.append(MessageSegment.face(305))

    for gid in __we_groups:
        await bot.send_group_msg(group_id=gid, message=msg)


@scheduler.scheduled_job('cron', hour=16, minute=50)
async def _():
    bot: CQHTTPBot = get_bot()

    msg = Message()
    msg.append(MessageSegment.text('让我看看是哪个乖乖还没有 We 重邮打卡 '))
    msg.append(MessageSegment.face(289))

    for gid in __we_groups:
        await bot.send_group_msg(group_id=gid, message=msg)