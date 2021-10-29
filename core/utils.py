import datetime
import json
import time

import requests
from bs4 import BeautifulSoup

# from core.models import YandexStatistic
from core.models import YandexStatistic

DATA_URL = "https://yandex.ru/news/top/region/Saint_Petersburg"
DATA_TEXT = "window.Ya=window.Ya||{};window.Ya.Neo=window.Ya.Neo||{};window.Ya.Neo.dataSource="
KEY = "ca93f5d4f09629870d64a2242ec9b61c"
PROXIES = []


def get_proxy():
    if len(PROXIES) == 0:
        try:
            time.sleep(1)
            new_proxy = requests.get(
                "https://api.best-proxies.ru/proxylist.json?key=%s&speed=1,2" % KEY,
                timeout=600)
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
                        type = 'socks4'
                    elif proxy['socks5']:
                        type = 'socks5'
                    PROXIES.append({"host": host, "port": port, "type": type})
            except Exception:
                pass
        except Exception:
            pass
        if len(PROXIES) == 0:
            time.sleep(60)
            return get_proxy()
    proxy = PROXIES.pop()
    session = generate_proxy_session(proxy.get("host"), proxy.get("port"), proxy.get("type"))
    if check_yandex_url(session):
        return session
    else:
        return get_proxy()


def check_yandex_url(session):
    try:
        response = session.get('https://newssearch.yandex.ru/news', timeout=15)
        if response.ok:
            return True
    except Exception:
        pass
    return False


def generate_proxy_session(proxy_host, proxy_port, proxy_type):
    session = requests.session()
    proxy_str = f"test:test@{proxy_host}:{proxy_port}"
    proxies = {'http': f'{proxy_type}://{proxy_str}', 'https': f'{proxy_type}://{proxy_str}'}

    session.proxies.update(proxies)
    return session


def get_response(new_session):
    try:
        new_response = new_session.get(DATA_URL).text
    except Exception:
        return get_response(get_proxy())
    if "captcha" in new_response:
        new_session = get_proxy()
        return get_response(new_session)
    return new_response, new_session


def get_yandex_data(session=None):
    if session is None:
        session = get_proxy()
    response, session = get_response(session)
    json_data = None
    for content in BeautifulSoup(response).find_all("script"):
        if DATA_TEXT in str(content):
            json_data = json.loads(str(content.contents[0]).replace(DATA_TEXT, "").strip()[:-1])
            break
    if json_data is not None:
        save_yandex_data(json_data)


def update_time_timezone(my_time):
    return my_time + datetime.timedelta(hours=3)


def save_yandex_data(json_data):
    yandex_story = []

    # now_time = datetime.now(timezone.utc)
    now_time = update_time_timezone(datetime.datetime.now())

    for story in json_data['news']['storyList']:
        yandex_story.append(
            YandexStatistic(
                id=str(story['id']),
                title=story['title'],
                url=story['url'],
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
    YandexStatistic.objects.bulk_create(yandex_story, batch_size=200)
