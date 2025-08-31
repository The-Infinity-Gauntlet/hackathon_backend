import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Explicitly wire broker and backend (env overrides settings if provided)
app.conf.broker_url = os.environ.get("CELERY_BROKER_URL") or "redis://redis_test:6379/0"
app.conf.result_backend = (
    os.environ.get("CELERY_RESULT_BACKEND") or "redis://redis_test:6379/1"
)
app.conf.timezone = os.environ.get("TZ", "America/Sao_Paulo")

app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'


# Ensure modules are imported in case autodiscover misses nested packages
try:
    __import__("core.users.app.tasks")
except Exception:  # pragma: no cover - best effort
    pass

# Ensure flood monitoring tasks are registered
try:
    __import__("core.flood_camera_monitoring.infra.tasks")
except Exception:  # pragma: no cover - best effort
    pass
