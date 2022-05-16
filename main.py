#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import asyncio
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
KEY = "ab5d05936452a51253d0a466fccf637e"
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
    from core.utils import get_yandex_data
    while True:
        try:
            print("start")

            get_yandex_data()
            time.sleep(60 * 10)
        except Exception as e:
            print(e)
    # loop = asyncio.new_event_loop()
    # login_result = loop.run_until_complete(asyncio.wait_for(get_yandex_data(), 6000))

    # main()
