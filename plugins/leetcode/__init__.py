from nonebot import on_command, export, require, get_bot
from nonebot.log import logger
from nonebot.adapters import Bot
from nonebot.adapters.cqhttp import GroupMessageEvent, MessageSegment, Message, Bot as CQHTTPBot, message
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

@scheduler.scheduled_job('cron', hour=0, minute=5)
@scheduler.scheduled_job('cron', hour=17, minute=0)
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

    