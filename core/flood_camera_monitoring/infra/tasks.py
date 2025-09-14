from celery import shared_task
import logging

from core.flood_camera_monitoring.tasks import (
    refresh_all_and_cache_task as _root_refresh,
)


@shared_task
def refresh_all_and_cache_task() -> int:
    """Compatibility wrapper to the canonical task in core.flood_camera_monitoring.tasks."""
    return _root_refresh()
