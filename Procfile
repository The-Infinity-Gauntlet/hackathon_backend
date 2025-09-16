web: gunicorn config.wsgi:application --timeout 120
worker: celery -A config worker -l info
beat: celery -A config beat --loglevel=INFO