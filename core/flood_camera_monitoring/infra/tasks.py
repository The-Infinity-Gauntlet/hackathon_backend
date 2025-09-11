from celery import shared_task
import logging


@shared_task
def analyze_all_cameras_task():
    from core.flood_camera_monitoring.application.use_cases.analyze_all_cameras import (
        AnalyzeAllCamerasService,
    )

    logger = logging.getLogger(__name__)
    service = AnalyzeAllCamerasService()
    saved = service.run()
    logger.info("AnalyzeAllCamerasTask finished: saved=%s", saved)
    return saved
