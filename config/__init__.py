"""Project package init.

Expose Celery app so `celery -A config ...` can discover it.
"""

from .celery import app as celery_app  # noqa: F401

__all__ = ("celery_app",)

