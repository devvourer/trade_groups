import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'sky_invest_trading.settings')

app = Celery('sky_invest_trading')

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
