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
KEY = "548b8a1d79d61255f79c01b47dd141c5"
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
            from core.models import PostGroupsGlobal

            PostGroupsGlobal.objects.create(id="e150ddbb07dca72fe51b1ea63c747a21",
                                            name="Стоимость квадратного метра в хрущёвках Петербурга упала на 30 тыс. рублей",
                                            url="https://dzen.ru/news/story/Stoimost_kvadratnogo_metra_vkhrushhyovkakh_Peterburga_upala_na30_tys._rublej--5078e5fd0867f34309d07f0e898422e0")
            print("start while true")
            get_yandex_data()
            print("stop")
        except Exception as e:
            print(f"Exception {e}")
    # loop = asyncio.new_event_loop()
    # login_result = loop.run_until_complete(asyncio.wait_for(get_yandex_data(), 6000))

    # main()
