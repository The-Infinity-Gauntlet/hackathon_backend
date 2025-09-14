import os
import logging
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

app.conf.beat_scheduler = "django_celery_beat.schedulers:DatabaseScheduler"

# Fallback: se migrações do django_celery_beat não foram aplicadas ainda, evita crash do beat
try:
    from django.db import connection  # type: ignore

    with connection.cursor() as cursor:  # type: ignore
        cursor.execute(
            "SELECT 1 FROM information_schema.tables WHERE table_name = %s",
            ["django_celery_beat_periodictask"],
        )
        exists = cursor.fetchone()
    if not exists:
        logging.getLogger(__name__).warning(
            "Tabelas django_celery_beat ausentes. Usando scheduler em memória padrão até aplicar as migrações."
        )
        app.conf.beat_scheduler = "celery.beat:PersistentScheduler"
except Exception:  # pragma: no cover - proteção defensiva
    pass


# Ensure modules are imported in case autodiscover misses nested packages
try:
    __import__("core.users.app.tasks")
except Exception:  # pragma: no cover - best effort
    pass

# Ensure flood monitoring tasks are registered
for mod in (
    "core.flood_camera_monitoring.tasks",
    "core.flood_camera_monitoring.infra.tasks",  # compat wrapper
):
    try:
        __import__(mod)
    except Exception:  # pragma: no cover - best effort
        pass
