from django.apps import AppConfig


class FloodCameraMonitoringConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.flood_camera_monitoring"
    label = "flood_camera_monitoring"
    verbose_name = "Flood Camera Monitoring"

    def ready(self):  # pragma: no cover
        # Ensure models are imported so Django registers them under this app
        try:
            from .infra import models  # noqa: F401
        except Exception:
            pass

        # Ensure Celery tasks are registered (worker may not autodiscover nested paths)
        try:
            from .infra import tasks  # noqa: F401
        except Exception:
            # Intencionalmente silencioso para não quebrar boot; logs do worker indicarão se faltar task
            pass
