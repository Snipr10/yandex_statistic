import json
import logging
from core.celery import app
from core.utils import get_yandex_data

logger = logging.getLogger(__file__)


@app.task
def start_task_new_update():
    print("start")
    get_yandex_data(source=1)


@app.task
def start_task_new_update2():
    print("start")
    get_yandex_data(source=2)


@app.task
def start_task():
    import requests
    try:
        print(requests.post("http://127.0.0.1:6000/api/text",headers={'Content-Type': 'application/json'}, data=json.dumps({
            "urls": "https://delovoe.tv/event/Minselhoz_ne_isklyuchaet_podorozhaniya_bezalkogolnih_napitkov/"
        })))
        print(requests.post("http://127.0.0.1:6000/api/text",headers={'Content-Type': 'application/json'}, data=json.dumps({
            "urls": "https://delovoe.tv/event/Minselhoz_ne_isklyuchaet_podorozhaniya_bezalkogolnih_napitkov/"
        })).text)
    except Exception as e:
        print(e)
