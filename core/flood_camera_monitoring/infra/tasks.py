from celery import shared_task
import logging
from core.common.cache import cache_set_json
from core.flood_camera_monitoring.application.use_cases.predict_all_cameras import (
    PredictAllCamerasService,
)


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


@shared_task
def refresh_predict_all_cache_task():
    """Compute PredictAllCamerasService and refresh cache key.

    Key: flood:predict_all
    """
    logger = logging.getLogger(__name__)
    service = PredictAllCamerasService()
    data = service.run()
    try:
        cache_set_json("flood:predict_all", {"data": data}, ex=300)
        logger.info(
            "Refreshed predict_all cache: items=%s",
            len(data) if isinstance(data, list) else "?",
        )
    except Exception as e:
        logger.warning("Failed to set predict_all cache: %s", e)
    return True
