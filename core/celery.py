import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'yandex_statistic.settings')

import django

django.setup()

app = Celery('yandex_statistic', include=['yandex_statistic.tasks'])
app.config_from_object('django.conf:settings')
app.autodiscover_tasks()

app.conf.beat_schedule = {

    'start_task_new_update': {
        'task': 'yandex_statistic.tasks.start_task_new_update',
        'schedule': crontab(minute='45')
    },
    'start_task': {
        'task': 'yandex_statistic.tasks.start_task',
        'schedule': crontab(minute='*/1')
    }
}
