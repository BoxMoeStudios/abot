from typing import Tuple
from nonebot import on_command, export
from nonebot.log import logger
from nonebot.adapters import Bot, Event
from hashlib import md5
from abot.setup import export_plugin
import random
import httpx
import re

_langs = {
    '中文': 'zh', '英语': 'en',
    '粤语': 'yue', '文言文': 'wyw', '日语': 'jp',
    '韩语': 'kor', '法语': 'fra', '西班牙语': 'spa',
    '泰语': 'th', '阿拉伯语': 'ara', '俄语': 'ru',
    '葡萄牙语': 'pt', '德语': 'de', '意大利语': 'it',
    '希腊语': 'el', '荷兰语': 'nl', '波兰语': 'pl',
    '保加利亚语': 'bul', '爱沙尼亚语': 'est', '丹麦语': 'dan',
    '芬兰语': 'fin', '捷克语': 'cs', '罗马尼亚语': 'rom',
    '斯洛文尼亚语': 'slo', '瑞典语': 'swe', '匈牙利语': 'hu',
    '繁体中文': 'cht', '越南语': 'vie'
}

__plugin_name__ = 'translate'
__plugin_usage__ = '''【翻译】
指定语言翻译:
/翻译.语言 内容
/fy.语言 内容

中英互译:
/翻译 内容
/fy 内容'''

export_plugin(export(), __plugin_name__, __plugin_usage__)

_appid = '20211211001024950'
_appkey = 'RJgY2Kk5HeBIoAZCXARw'
_url = 'http://api.fanyi.baidu.com/api/trans/vip/translate'
_headers = {'Content-Type': 'application/x-www-form-urlencoded'}


def make_md5(s: str, encoding='utf-8'):
    return md5(s.encode(encoding)).hexdigest()


async def fetch(query: str, lang: str):
    salt = random.randint(32768, 65536)
    sign = make_md5(_appid + query + str(salt) + _appkey)
    payload = {'appid': _appid, 'q': query, 'from': 'auto',
               'to': lang, 'salt': salt, 'sign': sign}
    async with httpx.AsyncClient() as c:
        result = await c.post(_url, params=payload, headers=_headers)
    return result.json()





translate = on_command(__plugin_name__, aliases={'翻译', 'fy'})

@translate.handle()
async def _(bot: Bot, event: Event):
    reply: str
    lang, text = get_lang_and_text(str(event.message))
    
    try:
        reply = (await fetch(text, lang)).get('trans_result')[0].get('dst')
    except Exception as e:
        reply = '翻译失败，后端跑路了啦～'
        logger.error(f'{e}')

    await translate.finish(reply, at_sender=True)


def get_lang_and_text(s: str) -> Tuple[str, str]:
    if not s.startswith('.'):
        return 'en' if has_cc(s) else 'zh', s

    i = s.find(' ')

    lang = s[1:i]
    if not re.match(r'[a-z]+', lang):
        lang = _langs[lang]

    return lang, s[i+1:]


def has_cc(s: str) -> bool:
    return re.match(r'[\u4e00-\u9fa5]', s) is not None