import logging
from core.celery import app
from core.utils import get_yandex_data

logger = logging.getLogger(__file__)


@app.task
def start_task_new_update():
    print("start")
    get_yandex_data()
