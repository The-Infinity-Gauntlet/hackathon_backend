from django.apps import AppConfig


class AddressingConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core.addressing"
    label = "addressing"
    verbose_name = "Addressing"

    def ready(self):  # pragma: no cover
        try:
            from .infra import models  # noqa: F401
        except Exception:
            pass
