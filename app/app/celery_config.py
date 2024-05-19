from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
import os

# Set the default Django settings module for the 'celery' program.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'app.app.settings')

# app = Celery('app')

# # Celery settings
app = Celery('app',
             broker='redis://localhost:6379/0',
             backend='redis://localhost:6379/0',
             include=['tracker.tasks'])


app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    'check_stock_every_minute': {
        'task': 'app.tracker.tasks.check_all_stock_availability',
        'schedule': crontab(minute='*/1'),
    },
}