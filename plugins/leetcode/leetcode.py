from typing import Dict, Set
from nonebot.adapters import Bot, Event
from httpx import AsyncClient
from bs4 import BeautifulSoup
from datetime import date
from random import choice
from abot.browser import get_ua



url_graphql = 'https://leetcode-cn.com/graphql'
url_to_get_cookie = 'https://leetcode-cn.com/problemset/all/'

query = '''query {
    todayRecord {
        question {
            questionFrontendId
            translatedTitle
            translatedContent
            difficulty
        }
    }
}'''

data = {
    'query': query
}

def make_headers(csrf: str) -> dict:
    return {
        'Content-Type': 'application/json',
        'x-csrftoken': csrf,
        'User-Agent': get_ua(),
        'Referer': 'https://leetcode-cn.com/problemset/all/',
        'Origin': 'https://leetcode-cn.com'
    }

async def fetch_today_question() -> dict:
    async with AsyncClient() as c:
        resp = await c.get(url_to_get_cookie)
        csrf = resp.cookies.get('csrftoken')
        if not csrf:
            raise ValueError('failed to get csrftoken')
        resp = await c.post(url_graphql, headers=make_headers(csrf), json=data)

    if resp.status_code != 200:
        raise ValueError(f'responded code {resp.status_code}')
    
    try:
        return resp.json()['data']['todayRecord'][0]['question']
    except KeyError as e:
        raise e
    except IndexError as e:
        raise e


__greets = ['今天刷题了吗？', '每日一题']

def _stringify(q: dict) -> str:
    content = q['translatedContent']
    title = q['translatedTitle']
    qid = q['questionFrontendId']
    soup = BeautifulSoup(content, 'html.parser')
    return (
        f'【{choice(__greets)}】'
        f'\n\n{qid}. {title}\n\n' + \
        soup.get_text().replace('\n\n', '\n')
    )

class Cache:
    cache: Dict[str, str] = {}
    blacklist: Set[int] = {711795626}

    @classmethod
    async def get_today_question(cls) -> str:
        today = date.today()
        key = f'{today.year}{today.month}{today.day}'

        question = cls.cache.get(key)
        if not question:
            question = _stringify(await fetch_today_question())
            cls.cache[key] = question

        return question

    @classmethod
    def subscribe(cls, gid: int):
        cls.blacklist.remove(gid)

    @classmethod
    def unsubscribe(cls, gid: int):
        cls.blacklist.add(gid)



        