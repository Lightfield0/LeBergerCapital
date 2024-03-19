FROM python:3.10
ENV PYTHONUNBUFFERED 1

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Statik dosyalar için dizin oluştur
RUN mkdir -p /app/staticfiles/

# Statik dosyaları topla
RUN python manage.py collectstatic --noinput

CMD gunicorn LeBergerCapital.wsgi:application --bind 0.0.0.0:8000
