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
        # 'schedule': crontab(hour='0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23',
        #                     minute='59')
        'schedule': crontab(minute='*/5')

    }
}
