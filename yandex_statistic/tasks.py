import logging
from yandex_statistic.celery.celery import app
from core.utils import get_yandex_data

logger = logging.getLogger(__file__)


@app.task
def start_task_new_update():
    get_yandex_data()
