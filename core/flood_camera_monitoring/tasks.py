from celery import shared_task
import logging

from core.common.cache import cache_set_json
from django.conf import settings


@shared_task
def refresh_all_and_cache_task() -> int:
    """Compute once via analyze service, persist alerts, and cache list for API."""
    from core.flood_camera_monitoring.application.use_cases.analyze_all_cameras import (
        AnalyzeAllCamerasService,
    )

    logger = logging.getLogger(__name__)
    try:
        # 1) Persist alerts (strong/medium) if thresholds met
        analyze = AnalyzeAllCamerasService()
        saved = analyze.run()

        # 2) Compute lightweight predictions list for caching/endpoint
        from core.flood_camera_monitoring.application.use_cases.predict_all_cameras import (
            PredictAllCamerasService,
        )

        predict = PredictAllCamerasService()
        data = predict.run()

        payload = {"data": data, "ts": int(__import__("time").time())}
        ttl = getattr(settings, "PREDICT_CACHE_TTL_SECONDS", 300)
        cache_set_json("flood:predict_all", payload, ex=int(ttl))
        logger.info(
            "Unified refresh done: cached=%d items, persisted=%d alerts",
            len(data),
            saved,
        )
        return len(data)
    except Exception:
        logger.exception("Unified refresh failed")
        return 0
