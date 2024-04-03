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
from core.models import YandexStatistic, YandexStatistic0, Post, ApiKeysModel, PostContentGlobal, PostGroupsGlobal

DATA_URL = "https://dzen.ru/news/top/region/Saint_Petersburg?issue_tld=ru"
DATA_TEXT = "window.Ya.Neo="
KEY = "9b3e4b2d01e913c233768debb0f0445c"
PROXIES = []

def get_proxy():
    if len(PROXIES) == 0:
        try:
            time.sleep(1)
            best_proxies_key =ApiKeysModel.objects.get(key="best_proxy").value

            # session.proxies.update(proxies)
            new_proxy = requests.get(
                "http://api.best-proxies.ru/proxylist.json?key=%s&type=http,https" % best_proxies_key,
                proxies={'http': f'http://tools-admin_metamap_com:456f634698@212.113.102.124:30001',
                         'https': f'http://tools-admin_metamap_com:456f634698@212.113.102.124:30001'})

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
        except Exception as e:
            print(f"get proxy: {e}")
        if len(PROXIES) == 0:
            time.sleep(7)
            return get_proxy()
    proxy = PROXIES.pop()
    session = generate_proxy_session(proxy.get("host"), proxy.get("port"), proxy.get("type"))
    session.headers["Cookie"] = 'zen_sso_checked=1; Session_id=noauth:;sso_checked=1;'
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
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
                'Accept-Language': 'ru-RU,ru;q=0.9',
                'Connection': 'keep-alive',
                'DNT': '1',
                'Referer': 'https://sso.dzen.ru/',
                'Sec-Fetch-Dest': 'document',
                'Sec-Fetch-Mode': 'navigate',
                'Sec-Fetch-Site': 'same-site',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/108.0.0.0 Mobile Safari/537.36',
                'sec-ch-ua': '"Not?A_Brand";v="8", "Chromium";v="108", "Google Chrome";v="108"',
                'sec-ch-ua-mobile': '?1',
                'sec-ch-ua-platform': '"Android"',
                'Cookie': 'zen_sso_checked=1; Session_id=noauth:;sso_checked=1;'
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
            str_json = (str(content.contents[0]).replace("window.Ya=window.Ya||{};window.Ya.Neo=window.Ya.Neo||{};window.Ya.Neo=", ""))
            while len(str_json)> 10:
                try:
                    json_data = json.loads(str_json)
                    json_data = json_data['dataSource']
                    break
                except Exception:
                    str_json = str_json[:-1]
            break
    i = 0
    if json_data is not None:
        logger_result = {}
        urls = []
        res = []
        for story in json_data['news']['storyList']:
            urls.append(story['url'].split("?")[0])
        for url in urls:
            i += 1
            url_full = url.replace("/story/", "/instory/")
            url_full = "https://dzen.ru" + url_full
            url_full = url_full.replace(urls[-1].split("/")[3], "news") + "?issue_tld=ru"
            response, session = get_response_news(session, url_full)

            script_ = None
            for script in BeautifulSoup(response).find_all("script"):
                if "nextPage" in str(script):
                    str_json = script.string[:-1].replace("window.Ya=window.Ya||{};window.Ya.Neo=window.Ya.Neo||{};window.Ya.Neo=", "")
                    script_ = json.loads(str_json+"}")
                    script_ = script_['dataSource']

                    break
            news = []
            # for new in script_.get('news',{}).get('instoryPage',[]):
            next_page = script_['news']['nextPage']
            try:
                for new in script_['news']['instoryPage']:
                    if new.get("docs"):
                        news.extend(new.get("docs"))
            except Exception as e:
                pass
            while next_page is not None:
                try:
                    response, session = get_response_news(session, "https://dzen.ru" + next_page + "&issue_tld=ru")
                    data = json.loads(response)["data"]
                    next_page = data['nextPage']
                    for new in data['instoryPage']:
                        if new.get("docs"):
                            news.extend(new.get("docs"))
                except Exception as e:
                    print(f"new page {e}")
            k = 0
            logger_result[url] = len(news)
            for new in news:
                k += 1
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
                    except Exception as e:
                        print(f"can not get text {e}")
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
                    print(f"newsE {e}")
        print("save")
        for k, i in logger_result.items():
            for story in json_data['news']['storyList']:
                url = story['url'].split("?")[0]
                if url == k:
                    print(f"{k} -- {i} -- {story['storyDocs']}")
        save_yandex_data(json_data, res, logger_result)
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


def send_to_rmq_full_test(rmq_json_data):
    try:
        parameters = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()

        channel.basic_publish(exchange='',
                              routing_key='smi_posts',
                              body=json.dumps(rmq_json_data))

    except Exception as e:
        print("can not send RMQ " + str(e))


def save_yandex_data(json_data, res, logger_result):
    yandex_story = []
    global_models = []
    # now_time = datetime.now(timezone.utc)
    now_time = update_time_timezone(datetime.datetime.now())

    posts = []
    posts_content = []
    d_set = set()

    try:
        parameters = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        for r in res:
            rmq_json_data = None
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
                    "keyword_id": 10000003,
                }

                channel.basic_publish(exchange='',
                                      routing_key='smi_posts',
                                      body=json.dumps(rmq_json_data))
                print(f"SEND RMQ {r.get('h_url')} {r.get('group_id')}")
                d_set.add(r.get("group_id"))

            except Exception as e:
                print("can not send RMQ " + str(e))
            send_to_rmq_full_test(rmq_json_data)
    except Exception as e:
        print(e)
    # if len(d_set) < 15:
    #     raise Exception("len(d_set)")
    result_group = {}
    for r in res:
        if result_group.get(r['group_id']) is not None:
            result_group.get(r['group_id']).append(r.get('h_url'))
        else:
            result_group[r['group_id']] = [r.get('h_url')]
    for story in json_data['news']['storyList']:
        url = story['url'].split("?")[0]
        try:
            yandex_story.append(
                YandexStatistic(
                    yandex_id=str(story['id']),
                    title=story['title'],
                    url=url,
                    lastHourDocs=story['lastHourDocs'],
                    storyDocs=logger_result.get(url, story['storyDocs']),
                    themeStories=story['themeStories'],
                    themeDocs=story['themeDocs'],
                    fullWatches=story.get('fullWatches') or 0,
                    regionalInterest=story['stat']['regionalInterest'],
                    generalInterest=story['stat']['generalInterest'],
                    weight=story['stat']['weight'],
                    parsing_date=now_time,
                    group_id=hashlib.md5(url.encode()).hexdigest()
                )
            )

            global_models.append(
                PostGroupsGlobal(
                    id=hashlib.md5(url.encode()).hexdigest(),
                    name=story['title'],
                    url=url
                )
            )
        except Exception as e:
            print(e)
    yandex_story_o = []

    for story in json_data['news']['storyList']:
        url = story['url'].split("?")[0]
        try:
            yandex_story_o.append(
                YandexStatistic0(
                    yandex_id=str(story['id']),
                    title=story['title'],
                    url=url,
                    lastHourDocs=story['lastHourDocs'],
                    storyDocs=logger_result.get(url, story['storyDocs']),
                    themeStories=story['themeStories'],
                    themeDocs=story['themeDocs'],
                    fullWatches=story.get('fullWatches') or 0,
                    regionalInterest=story['stat']['regionalInterest'],
                    generalInterest=story['stat']['generalInterest'],
                    weight=story['stat']['weight'],
                    parsing_date=now_time,
                    group_id=hashlib.md5(url.encode()).hexdigest()

                )
            )
        except Exception as e:
            print(e)
    # #     posts.append(
    # #         Post(
    # #             cache_id=get_sphinx_id_16(r['h_url']),
    # #             owner_sphinx_id=get_sphinx_id("http://" + r['h_url'].split("/")[2]),
    # #             created=datetime.datetime.now(),
    # #             group_id=r['group_id'])
    # #     )
    # #     posts_content.append(
    # #         PostContentGlobal(
    # #             cache_id=get_sphinx_id_16(r['h_url']),
    # #             content=r['text'],
    # #             title=r['title'],
    # #             link=r['h_url'])
    # #     )
    # print("=====================RESULT======================")
    # print(result_group)
    # print("=====================RESULT END======================")
    django.db.close_old_connections()

    # time.sleep(60 * 10)
    #
    # forgot_story = []
    # for k, v in result_group.items():
    #     if not checker(k):
    #         forgot_story.append(k)
    #         add_again(res, k)
    # if len(forgot_story) > 0:
    #     time.sleep(60 * 5)
    # for k in forgot_story:
    #     if not checker(k):
    #         raise Exception("can not find story")
    try:
        PostGroupsGlobal.objects.bulk_create(global_models, batch_size=200, ignore_conflicts=True)
        save_group(global_models)
    except Exception:
        save_group(global_models)

    django.db.close_old_connections()

    # try:
    #     Post.objects.bulk_create(posts, batch_size=200, ignore_conflicts=True)
    #     PostContentGlobal.objects.bulk_create(posts_content, batch_size=200, ignore_conflicts=True)
    # except Exception as e:
    #     print(e)

    print("YandexStatistic")
    YandexStatistic.objects.all().delete()
    try:
        YandexStatistic.objects.bulk_create(yandex_story, batch_size=200, ignore_conflicts=True)
    except Exception:
        try:
            YandexStatistic.objects.bulk_create(yandex_story, batch_size=200)
        except Exception:
            pass
    try:
        YandexStatistic0.objects.bulk_create(yandex_story_o, batch_size=200, ignore_conflicts=True)
    except Exception:
        try:
            YandexStatistic0.objects.bulk_create(yandex_story_o, batch_size=200)
        except Exception:
            pass
    try:
        django.db.close_old_connections()
    except Exception:
        pass
    non_stop = True
    attempt = 0
    while non_stop and attempt < 10:
        try:
            PostGroupsGlobal.objects.bulk_create(global_models, batch_size=200, ignore_conflicts=True)
            non_stop = False
        except Exception:
            pass
        save_group(global_models)
        attempt += 1


def add_again(res, group_id):
    try:
        parameters = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
        connection = pika.BlockingConnection(parameters=parameters)
        channel = connection.channel()
        for r in res:
            if r.get("group_id") == group_id:
                try:
                    rmq_json_data = {
                        "title": r.get('title', ''),
                        "content": r.get("text", ""),
                        "created": r.get('date_').strftime("%Y-%m-%d %H:%M:%S"),
                        "url": r.get('h_url'),
                        "author_name": r.get("author_name", ""),
                        "author_icon": r.get("author_icon", ""),
                        "group_id": r.get("group_id"),
                        "images": [],
                        "keyword_id": 10000003,
                    }

                    channel.basic_publish(exchange='',
                                          routing_key='smi_posts',
                                          body=json.dumps(rmq_json_data))
                    print(f"SEND RMQ {r.get('h_url')} {r.get('group_id')}")

                except Exception as e:
                    print("can not send RMQ " + str(e))
    except Exception as e:
        print(e)


def checker(r, attempt=0):
    try:
        p = Post.objects.filter(group_id=r)
        if len(p) > 0:
            return True
    except Exception:
        pass
    time.sleep(30)
    if attempt > 2:
        return False
    return checker(r, attempt + 1)


def save_group(global_models):
    for g in global_models:
        try:
            g.save()
        except Exception:
            try:
                g.save()
            except Exception:
                pass
    # try:
    #     Post.objects.bulk_update(posts, ['updated', 'group_id'], batch_size=200)
    # except Exception as e:
    #     print(e)
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
