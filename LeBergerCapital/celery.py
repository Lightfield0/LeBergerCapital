# projenizin_ana_dizini/celery.py

import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'LeBergerCapital.settings')

app = Celery('LeBergerCapital')

app.config_from_object('django.conf:settings', namespace='CELERY')

# Django ile oluşturulan tüm task'ları otomatik olarak keşfetmek için:
app.autodiscover_tasks()
