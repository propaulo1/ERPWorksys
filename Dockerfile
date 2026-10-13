# Imagem base Debian (x86-64 genérico): roda no Xeon X5690 sem AVX.
FROM python:3.13-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
RUN DJANGO_DEBUG=0 DJANGO_SECRET_KEY=build python manage.py collectstatic --noinput \
    && useradd --system --uid 1000 erp \
    && mkdir -p /app/media && chown erp /app/media
USER erp

EXPOSE 8000
CMD ["sh", "-c", "python manage.py migrate --noinput && gunicorn config.wsgi:application --bind 0.0.0.0:8000 --workers 3 --timeout 120 --access-logfile -"]
