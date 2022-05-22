import datetime
import hashlib
import json
import time

import pika as pika
import requests
from bs4 import BeautifulSoup
from dateutil.parser import parse
import django.db

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
            time.sleep(2)
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
    new_response = None
    while True and new_response is None:
        try:
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
                new_response = new_session.get(url, headers=headers, timeout=15).text
            except Exception as e:
                print(url)
                print(new_session.proxies)
                print(f"get_response_news1 {e}")
                new_session = get_proxy()

                # return get_response_news(get_proxy(), url)
            if new_response is not None and "captcha" in new_response:
                new_response = None
                new_session = get_proxy()
                # return get_response_news(new_session, url)
        except Exception as e:
            print(f"get_response_news2 {e}")
            new_response = None
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
    i = 0
    if json_data is not None:
        urls = []
        res = []
        for story in json_data['news']['storyList']:
            urls.append(story['url'].split("?")[0])
        print(f"URLS SIZE {len(urls)}")
        for url in urls:
            i += 1
            print(f"i {i}")
            url_full = url.replace("/story/", "/instory/")
            response, session = get_response_news(session, url_full)

            script_ = None
            for script in BeautifulSoup(response).find_all("script"):
                if "window.Ya.Neo.dataSource" in str(script):
                    script_ = json.loads(script.string[:-1].replace("window.Ya.Neo.dataSource=", ""))
                    break
            news = []
            for new in script_['news']['instoryPage']:
                if new.get("docs"):
                    news.extend(new.get("docs"))
            print(f"news {len(news)}")
            k = 0
            for new in news:
                k += 1
                print(f"k {k}")
                try:
                    text = new['text'][-1]["text"]
                    title = new['title'][0]['text']
                    try:
                        date_ = parse(new['time'])
                    except Exception as e:
                        date_ = datetime.datetime.now()
                    author_name = new['sourceName']
                    author_icon = new['image']
                    h_url = new['url'].split("?")[0]
                    try:
                        new_text = requests.post("http://127.0.0.1:6000/api/text",
                                                 headers={'Content-Type': 'application/json'},
                                                 data=json.dumps({"urls": h_url})).text
                        if new_text:
                            text = new_text
                    except Exception:
                        print("text")
                    res.append(
                        {
                            "date_": date_,
                            "text": text,
                            "title": title,
                            "h_url": h_url,
                            "group_id": hashlib.md5(url.encode()).hexdigest(),
                            "author_name": author_name,
                            "author_icon": author_icon
                        }
                    )
                except Exception as e:
                    print(e)
        print("save")
        save_yandex_data(json_data, res)
        # for data in BeautifulSoup(response).find_all("div", {"class": "mg-snippet mg-snippet_flat news-search-story__snippet"}):
        #     try:
        #         text = data.find("span", {"class": "mg-snippet__text"}).text
        #         title = data.find("div", {"class": "mg-snippet__title"}).text
        #         try:
        #             date_ = parse(data.find("span", {"class": "mg-snippet-source-info__time"}).text)
        #         except Exception as e:
        #             date_ = datetime.datetime.now()
        #         author_name = data.find("span", {"class": "mg-snippet-source-info__agency-name"}).text
        #         author_icon = data.find("img", {"class": "neo-image neo-image_loaded"}).text
        #         h_url = data.find("a", {"class": "mg-snippet__url"}).get("href").split("?")[0]
        #         try:
        #             new_text = requests.post("http://127.0.0.1:6000/api/text",
        #                                      headers={'Content-Type': 'application/json'},
        #                                      data=json.dumps({"urls": h_url})).text
        #             if new_text:
        #                 text = new_text
        #         except Exception:
        #             pass
        #         res.append(
        #             {
        #                 "date_": date_,
        #                 "text": text,
        #                 "title": title,
        #                 "h_url": h_url,
        #                 "group_id": hashlib.md5(url.encode()).hexdigest()
        #             }
        #         )
        #     except Exception as e:
        #         print(e)


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
    try:
        parameters = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        for r in res:
            try:
                rmq_json_data = {
                    "title": r.get('title', ''),
                    "content": r.get("text"),
                    "created": r.get('date_').strftime("%Y-%m-%d %H:%M:%S"),
                    "url": r.get('h_url'),
                    "author_name": r.get("author_name"),
                    "author_icon": r.get("author_icon"),
                    "group_id": r.get("group_id"),
                    "images": [],
                    "keyword_id": 10000005,
                }

                channel.basic_publish(exchange='',
                                      routing_key='smi_posts',
                                      body=json.dumps(rmq_json_data))
                print("SEND RMQ")

            except Exception as e:
                print("can not send RMQ " + str(e))
    except Exception as e:
        print(e)
    for r in res:
        print(r['group_id'])
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
    django.db.close_old_connections()

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
    # try:
    #     PostContentGlobal.objects.bulk_update(posts_content, ['content', ], batch_size=200)
    # except Exception as e:
    #     print(e)


def get_sphinx_id(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest()[:16], 16)))


def get_sphinx_id_16(url):
    m = hashlib.md5()
    m.update(url.encode())
    return int(str(int(m.hexdigest()[:16], 16))[:16])
