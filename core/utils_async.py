import asyncio
import datetime
import json
import time

import httpx as httpx
import requests
from bs4 import BeautifulSoup

# from core.models import YandexStatistic
from core.models import YandexStatistic, YandexStatistic0

DATA_URL = "https://yandex.ru/news/top/region/Saint_Petersburg"
DATA_TEXT = "window.Ya.Neo.dataSource="
KEY = "f0572bd7a7a6813fed71a5c5269cc209"
PROXIES = []


async def get_proxy_async():
    if len(PROXIES) == 0:
        try:
            await asyncio.sleep(1)
            client = httpx.AsyncClient()

            new_proxy = await client.get(
                "https://api.best-proxies.ru/proxylist.json?key=%s&speed=1,2" % KEY,
                timeout=600)
            await client.aclose()

            try:
                for proxy in json.loads(new_proxy.text):
                    host = proxy['ip']
                    port = proxy['port']
                    type = None
                    if proxy['http']:
                        type = 'http'
                    elif proxy['https']:
                        type = 'https'
                    elif proxy['socks4']:
                        type = 'socks5'
                    elif proxy['socks5']:
                        type = 'socks5'
                    PROXIES.append({"host": host, "port": port, "type": type})
            except Exception:
                pass
        except Exception:
            pass
        if len(PROXIES) == 0:
            await asyncio.sleep(30)
            return await get_proxy_async()
    while PROXIES:
        proxy = PROXIES.pop()
        print(proxy)
        session = await generate_proxy_session_async(proxy.get("host"), proxy.get("port"), proxy.get("type"))
        if await check_yandex_url(session):
            return session
    return await get_proxy_async()


async def check_yandex_url(session):
    try:
        response = await session.get('https://newssearch.yandex.ru/news', timeout=8)
        if response.status_code == 200:
            return True
    except Exception as e:
        print(e)
    try:
        await session.aclose()
    except Exception as e:
        print(e)
    return False


async def generate_proxy_session_async(proxy_host, proxy_port, proxy_type):
    proxy_str = f"{proxy_host}:{proxy_port}"
    proxies = {'http://': f'{proxy_type}://{proxy_str}', 'https://': f'{proxy_type}://{proxy_str}'}
    session = httpx.AsyncClient(proxies=proxies)

    return session


async def get_response_news_async(new_session, url):
    headers = {
        'authority': 'yandex.ru',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'accept-language': 'ru-RU,ru;q=0.9',
        'dnt': '1',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Linux"',
        'sec-fetch-dest': 'document',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-site': 'none',
        'sec-fetch-user': '?1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'
    }

    try:
        new_resp = await new_session.get(url, headers=headers, timeout=60)
        new_response = new_resp.text
    except Exception as e:
        try:
            await new_session.aclose()
        except Exception:
            pass
        new_session = await get_proxy_async()
        return await get_response_news_async(new_session, url)
    if new_resp.status_code != 200 or "captcha" in new_response:
        try:
            await new_session.aclose()
        except Exception:
            pass
        new_session = await get_proxy_async()
        return await get_response_news_async(new_session, url)
    return new_response, new_session


async def get_yandex_data(session=None):
    if session is None:
        from core.utils import get_proxy
        session = get_proxy()
    from core.utils import get_response
    response, session = get_response(session)
    json_data = None
    for content in BeautifulSoup(response).find_all("script"):
        if DATA_TEXT in str(content):
            json_data = json.loads(str(content.contents[0]).replace(DATA_TEXT, "").strip()[:-1])
            break
    if json_data is not None:
        urls = []
        for story in json_data['news']['storyList']:
            urls.append(story['url'].split("?")[0])
        tasks = [response_news_async(url) for url in urls]
        res = await asyncio.gather(*tasks)
        save_yandex_data(json_data)


async def response_news_async(url):
    res = []
    url_full = url.replace("/story/", "/instory/")
    print(url_full)
    new_session = await get_proxy_async()

    response, session = await get_response_news_async(new_session, url_full)

    for data in BeautifulSoup(response).find_all("div", {"class": "mg-snippet__content"}):
        res.append(data)
    print(res)
    return {
        "url": url,
        "data": res
    }


def update_time_timezone(my_time):
    return my_time + datetime.timedelta(hours=3)


def save_yandex_data(json_data):
    yandex_story = []

    # now_time = datetime.now(timezone.utc)
    now_time = update_time_timezone(datetime.datetime.now())

    for story in json_data['news']['storyList']:
        yandex_story.append(
            YandexStatistic(
                yandex_id=str(story['id']),
                title=story['title'],
                url=story['url'].split("?")[0],
                lastHourDocs=story['lastHourDocs'],
                storyDocs=story['storyDocs'],
                themeStories=story['themeStories'],
                themeDocs=story['themeDocs'],
                fullWatches=story['fullWatches'],
                regionalInterest=story['stat']['regionalInterest'],
                generalInterest=story['stat']['generalInterest'],
                weight=story['stat']['weight'],
                parsing_date=now_time
            )
        )
    yandex_story_o = []

    for story in json_data['news']['storyList']:
        yandex_story_o.append(
            YandexStatistic0(
                yandex_id=str(story['id']),
                title=story['title'],
                url=story['url'].split("?")[0],
                lastHourDocs=story['lastHourDocs'],
                storyDocs=story['storyDocs'],
                themeStories=story['themeStories'],
                themeDocs=story['themeDocs'],
                fullWatches=story['fullWatches'],
                regionalInterest=story['stat']['regionalInterest'],
                generalInterest=story['stat']['generalInterest'],
                weight=story['stat']['weight'],
                parsing_date=now_time
            )
        )
    YandexStatistic.objects.all().delete()
    YandexStatistic.objects.bulk_create(yandex_story, batch_size=200)
    YandexStatistic0.objects.bulk_create(yandex_story_o, batch_size=200)
