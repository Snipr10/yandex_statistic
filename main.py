#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import asyncio
import hashlib
import json
import os
import sys
import time

import pika
from bs4 import BeautifulSoup



def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yandex_statistic.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)



DATA_URL = "https://yandex.ru/news/top/region/Saint_Petersburg"
DATA_TEXT = "window.Ya.Neo.dataSource="
PROXIES = []



if __name__ == '__main__':

    import requests
    import json

    # url = "http://localhost:8000/api/text"
    # headers =
    # payload = json.dumps({
    #     "urls": "https://delovoe.tv/event/Minselhoz_ne_isklyuchaet_podorozhaniya_bezalkogolnih_napitkov/"
    # })
    #
    # response = requests.request("POST", url,, data=payload)
    # main()
    # import requests
    # os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yandex_statistic.settings')
    # try:
    #     from django.core.management import execute_from_command_line
    # except ImportError as exc:
    #     raise ImportError(
    #         "Couldn't import Django. Are you sure it's installed and "
    #         "available on your PYTHONPATH environment variable? Did you "
    #         "forget to activate a virtual environment?"
    #     ) from exc
    print(1)
    import django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yandex_statistic.settings')
    # parameters = pika.URLParameters("amqp://full_posts_parser:nJ6A07XT5PgY@192.168.5.46:5672/smi_tasks")
    # connection = pika.BlockingConnection(parameters=parameters)
    # channel = connection.channel()
    django.setup()
    from core.utils import get_yandex_data, get_proxy
    from core.models import PostGroupsGlobal
    url = "https://dzen.ru/news/story/Moshenniki_vymanili_13_millionov_rublej_upensionerki_izMurino--ac262d19bfa00d76b8afad78dd9b2d47"
    print(url)
    proxy = get_proxy()
    print(url)

    # get_yandex_data()
    # global_models = []
    # global_models.append(
    #     PostGroupsGlobal(
    #         id=hashlib.md5(url.encode()).hexdigest(),
    #         name="Мошенники выманили 13 миллионов рублей у пенсионерки из Мурино",
    #         url=url
    #     )
    # )
    # PostGroupsGlobal.objects.bulk_create(global_models, batch_size=200, ignore_conflicts=True)
    # print("done")
    #
    # # loop = asyncio.new_event_loop()
    # # login_result = loop.run_until_complete(asyncio.wait_for(get_yandex_data(), 6000))
    #
    # # main()
