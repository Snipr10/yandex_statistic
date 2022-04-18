import datetime
import hashlib
import json
import time

import requests
from bs4 import BeautifulSoup

# from core.models import YandexStatistic
from core.models import YandexStatistic, YandexStatistic0, Post, PostContentGlobal

DATA_URL = "https://yandex.ru/news/top/region/Saint_Petersburg"
DATA_TEXT = "window.Ya.Neo.dataSource="
KEY = "ab5d05936452a51253d0a466fccf637e"
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
                        PROXIES.append({"host": host, "port": port, "type": type})

                    elif proxy['https']:
                        type = 'https'
                        PROXIES.append({"host": host, "port": port, "type": type})

                    elif proxy['socks4']:
                        type = 'socks4'
                    elif proxy['socks5']:
                        type = 'socks5'
                    # PROXIES.append({"host": host, "port": port, "type": type})
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
        response = session.get('https://newssearch.yandex.ru/news', timeout=5)
        if response.ok:
            return True
    except Exception as e:
        pass
    return False


def generate_proxy_session(proxy_host, proxy_port, proxy_type):
    session = requests.session()
    proxy_str = f"{proxy_host}:{proxy_port}"
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


def get_response_news(new_session, url):
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
        new_response = new_session.get(url, headers=headers).text
    except Exception as e:
        return get_response_news(get_proxy(), url)
    if "captcha" in new_response:
        new_session = get_proxy()
        return get_response_news(new_session, url)
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
        urls = []
        res = []
        for story in json_data['news']['storyList']:
            urls.append(story['url'].split("?")[0])
        for url in urls:
            url_full = url.replace("/story/", "/instory/")
            response, session = get_response_news(session, url_full)

            for data in BeautifulSoup(response).find_all("div", {"class": "mg-snippet__content"}):
                try:
                    text = data.find("span", {"class": "mg-snippet__text"}).text
                    title = data.find("div", {"class": "mg-snippet__title"}).text
                    h_url = data.find("a", {"class": "mg-snippet__url"}).get("href").split("?")[0]
                    res.append(
                        {
                            "text": text,
                            "title": title,
                            "h_url": h_url,
                            "group_id": hashlib.md5(url.encode()).hexdigest()
                        }
                    )
                except Exception as e:
                    print(e)
            print(response)

        save_yandex_data(json_data, res)


def update_time_timezone(my_time):
    return my_time + datetime.timedelta(hours=3)


def save_yandex_data(json_data, res):
    yandex_story = []

    # now_time = datetime.now(timezone.utc)
    now_time = update_time_timezone(datetime.datetime.now())

    for story in json_data['news']['storyList']:
        url = story['url'].split("?")[0]
        yandex_story.append(
            YandexStatistic(
                yandex_id=str(story['id']),
                title=story['title'],
                url=url,
                lastHourDocs=story['lastHourDocs'],
                storyDocs=story['storyDocs'],
                themeStories=story['themeStories'],
                themeDocs=story['themeDocs'],
                fullWatches=story['fullWatches'],
                regionalInterest=story['stat']['regionalInterest'],
                generalInterest=story['stat']['generalInterest'],
                weight=story['stat']['weight'],
                parsing_date=now_time,
                group_id=hashlib.md5(url.encode()).hexdigest()
            )
        )
    yandex_story_o = []

    for story in json_data['news']['storyList']:
        url = story['url'].split("?")[0]

        yandex_story_o.append(
            YandexStatistic0(
                yandex_id=str(story['id']),
                title=story['title'],
                url=url,
                lastHourDocs=story['lastHourDocs'],
                storyDocs=story['storyDocs'],
                themeStories=story['themeStories'],
                themeDocs=story['themeDocs'],
                fullWatches=story['fullWatches'],
                regionalInterest=story['stat']['regionalInterest'],
                generalInterest=story['stat']['generalInterest'],
                weight=story['stat']['weight'],
                parsing_date=now_time,
                group_id=hashlib.md5(url.encode()).hexdigest()

            )
        )
    posts = []
    posts_content = []

    for r in res:
        posts.append(
            Post(
                cache_id=get_sphinx_id_16(r['h_url']),
                owner_sphinx_id=get_sphinx_id("http://" + r['h_url'].split("/")[2]),
                created=datetime.datetime.now(),
                group_id=r['group_id'])
        )
        posts_content.append(
            PostContentGlobal(
                cache_id=get_sphinx_id_16(r['h_url']),
                content=r['text'],
                title=r['title'],
                link=r['h_url'])
        )
    try:
        Post.objects.bulk_create(posts, batch_size=200, ignore_conflicts=True)
        PostContentGlobal.objects.bulk_create(posts_content, batch_size=200, ignore_conflicts=True)
    except Exception as e:
        print(e)
    YandexStatistic.objects.all().delete()
    YandexStatistic.objects.bulk_create(yandex_story, batch_size=200)
    YandexStatistic0.objects.bulk_create(yandex_story_o, batch_size=200)

    try:
        Post.objects.bulk_update(posts, ['updated', ], batch_size=200)
    except Exception as e:
        print(e)
    try:
        PostContentGlobal.objects.bulk_update(posts_content, ['content', ], batch_size=200)
    except Exception as e:
        print(e)


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest()[:16], 16)))


def get_sphinx_id_16(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest()[:16], 16))[:16])
