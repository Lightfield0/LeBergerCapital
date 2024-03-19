FROM python:3.10
ENV PYTHONUNBUFFERED 1

# Çalışma dizinini belirle
WORKDIR /app

# Gerekli Python paketlerini yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Proje dosyalarını kopyala
COPY . .

# Statik dosyaları topla
RUN python manage.py collectstatic

# Uygulamayı çalıştır
CMD gunicorn LeBergerCapital.wsgi:application --bind 0.0.0.0:8000
