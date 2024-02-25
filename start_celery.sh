#!/bin/sh

# Django ayarlarını belirtin
export DJANGO_SETTINGS_MODULE=LeBergerCapital.settings

# Redis URL'ini belirtin (örnek amaçlıdır, gerçek URL'nizi kullanın)
export CELERY_BROKER_URL=redis://localhost:6379/0

# Celery worker'ı başlat
celery -A LeBergerCapital worker -l info &

# Celery beat'i başlat
celery -A LeBergerCapital beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler &


# chmod +x start_celery.sh