from celery import shared_task
import logging


@shared_task
def refresh_predict_all_cache_task() -> int:
    """Compute predictions for all cameras and refresh the shared cache.

    Stores under key 'flood:predict_all' a JSON payload {"data": [...], "ts": <unix>}
    Returns the number of camera entries computed.
    """
    from core.flood_camera_monitoring.application.use_cases.predict_all_cameras import (
        PredictAllCamerasService,
    )
    from core.common.cache import cache_set_json, now_ts

    logger = logging.getLogger(__name__)
    service = PredictAllCamerasService()
    data = service.run()
    cache_set_json("flood:predict_all", {"data": data, "ts": now_ts()}, ex=120)
    logger.info("Refreshed predict_all cache with %s entries", len(data))
    return len(data)


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
