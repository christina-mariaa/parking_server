from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parking_server.settings')
app = Celery('parking_server')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()  # Автоматически загружаем задачи из всех приложений

app.conf.beat_schedule = {
    'complete-expired-bookings-every-minute': {
        'task': 'api.tasks.manage_expired_and_unpaid_bookings',
        'schedule': crontab(minute='*/1'),
	'options': {
            'expires': 60,  
        },
    },
}
