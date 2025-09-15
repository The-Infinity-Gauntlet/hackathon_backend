from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from core.flood_camera_monitoring.presentation.serializers import (
    StreamSnapshotSerializer,
    StreamBatchSerializer,
)
from django.conf import settings
from core.flood_camera_monitoring.presentation.utils import build_prediction_payload
from core.flood_camera_monitoring.adapters.gateways.opencv_stream_adapter import (
    OpenCVVideoStream,
)
from core.flood_camera_monitoring.infra.torch_flood_classifier import (
    build_default_classifier,
)
from core.flood_camera_monitoring.application.use_cases.detect_flood_from_stream import (
    DetectFloodFromStream,
)
from core.flood_camera_monitoring.application.use_cases.detect_flood_snapshot_from_stream import (
    DetectFloodSnapshotFromStream,
)
from core.flood_camera_monitoring.application.dto.stream_request import (
    StreamDetectRequest,
)
from core.common.cache import cache_get_json
from core.flood_camera_monitoring.infra.tasks import refresh_predict_all_cache_task
from core.flood_camera_monitoring.application.dto.snapshot_request import (
    SnapshotDetectRequest,
)
from core.flood_camera_monitoring.application.use_cases.analyze_all_cameras import (
    AnalyzeAllCamerasService,
)
from core.flood_camera_monitoring.application.use_cases.predict_all_cameras import (
    PredictAllCamerasService,
)
from core.flood_camera_monitoring.infra.models import Camera
import uuid
from config.pagination import DefaultPageNumberPagination
from core.common.mixins import SafeOrderingMixin
from pathlib import Path
from django.db import connections
import os
import redis


class FloodMonitoringViewSet(SafeOrderingMixin, viewsets.ViewSet):
    # Ordering config for cameras list
    ordering_map = {
        "description": "description",
        "created_at": "created_at",
        "updated_at": "updated_at",
        "status": "status",
        "neighborhood": "neighborhood__name",
        "region": "neighborhood__region__name",
        "latitude": "latitude",
        "longitude": "longitude",
    }
    default_ordering = "description"

    @action(detail=False, methods=["get"], url_path="health")
    def health(self, request):
        env_path = os.getenv("FLOOD_MODEL_PATH")
        if env_path:
            checkpoint_path = Path(env_path)
        else:
            checkpoint_path = (
                Path(__file__).resolve().parents[2]
                / "infra"
                / "machine_model"
                / "best_real_model.pth"
            )

        def looks_like_lfs_pointer(p: Path) -> bool:
            try:
                with p.open("rb") as fh:
                    head = fh.read(256)
                return head.startswith(b"version https://git-lfs.github.com")
            except Exception:
                return False

        model_exists = checkpoint_path.exists() and checkpoint_path.is_file()
        model_size = 0
        if model_exists:
            try:
                model_size = checkpoint_path.stat().st_size
            except Exception:
                model_size = 0
        model_ok = bool(
            model_exists
            and (model_size >= 1024 * 1024)
            and not looks_like_lfs_pointer(checkpoint_path)
        )

        # DB
        db_ok = False
        db_error = None
        try:
            with connections["default"].cursor() as cur:
                cur.execute("SELECT 1")
                cur.fetchone()
            db_ok = True
        except Exception as e:
            db_error = str(e)

        # Redis broker
        redis_ok = False
        redis_error = None
        redis_url = getattr(settings, "CELERY_BROKER_URL", "redis://redis:6379/0")
        try:
            r = redis.from_url(redis_url)
            if r.ping():
                redis_ok = True
        except Exception as e:
            redis_error = str(e)

        all_ok = model_ok and db_ok and redis_ok
        payload = {
            "status": "ok" if all_ok else "degraded",
            "model": {
                "ok": model_ok,
                "path": str(checkpoint_path),
                "exists": model_exists,
                "size": model_size,
            },
            "database": {"ok": db_ok, **({"error": db_error} if db_error else {})},
            "redis": {
                "ok": redis_ok,
                "url": redis_url,
                **({"error": redis_error} if redis_error else {}),
            },
        }
        return Response(
            payload,
            status=(
                status.HTTP_200_OK if all_ok else status.HTTP_503_SERVICE_UNAVAILABLE
            ),
        )

    @action(detail=False, methods=["get"], url_path="predict/all")
    def predict_all(self, request):
        force_refresh = str(request.query_params.get("refresh", "false")).lower() in (
            "1",
            "true",
            "yes",
        )
        cached = None if force_refresh else cache_get_json("flood:predict_all")
        if cached and isinstance(cached, dict) and "data" in cached:
            data = cached["data"]
        else:
            service = PredictAllCamerasService()
            data = service.run()
            try:
                refresh_predict_all_cache_task.delay()
            except Exception:
                pass

        # optional sorting of in-memory results
        ordering_param = request.query_params.get("ordering", "description")
        order_map = {
            "description": lambda it: (it.get("camera") or {}).get("description") or "",
            "is_flooded": lambda it: bool(it.get("is_flooded", False)),
            "confidence": lambda it: float(it.get("confidence", 0.0)),
            "normal": lambda it: float(
                (it.get("probabilities") or {}).get("normal", 0.0)
            ),
            "flooded": lambda it: float(
                (it.get("probabilities") or {}).get("flooded", 0.0)
            ),
            "medium": lambda it: float(
                (it.get("probabilities") or {}).get("medium", 0.0)
            ),
        }
        if ordering_param:
            parts = [p.strip() for p in str(ordering_param).split(",") if p.strip()]
            parsed = []
            for p in parts:
                desc = p.startswith("-")
                key = p[1:] if desc else p
                fn = order_map.get(key)
                if fn:
                    parsed.append((fn, desc))
            for fn, desc in reversed(parsed):
                try:
                    data.sort(key=fn, reverse=desc)
                except Exception:
                    pass

        paginator = DefaultPageNumberPagination()
        page_items = paginator.paginate_queryset(data, request, view=self)
        return paginator.get_paginated_response(page_items)

    @action(detail=False, methods=["post"], url_path="predict/snapshot")
    def predict_snapshot(self, request):
        serializer = StreamSnapshotSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        clf = build_default_classifier()
        stream = OpenCVVideoStream(data["stream_url"])  # implements VideoStreamPort
        service = DetectFloodSnapshotFromStream(classifier=clf, stream=stream)
        try:
            res = service.execute(
                SnapshotDetectRequest(
                    timeout_seconds=float(data.get("timeout_seconds", 5.0))
                )
            )
        except TimeoutError:
            return Response(
                {"detail": "Could not capture frame"},
                status=status.HTTP_504_GATEWAY_TIMEOUT,
            )

        return Response(build_prediction_payload(res))

    @action(detail=False, methods=["post"], url_path="predict/batch")
    def predict_batch(self, request):
        serializer = StreamBatchSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        clf = build_default_classifier()
        stream = OpenCVVideoStream(data["stream_url"])  # VideoStreamPort
        service = DetectFloodFromStream(classifier=clf, stream=stream)
        req = StreamDetectRequest(
            stream_url=data["stream_url"],
            interval_seconds=float(data.get("interval_seconds", 2.0)),
            max_iterations=int(data.get("max_iterations", 3)),
        )

        results = [build_prediction_payload(res) for res in service.run(req)]

        return Response({"results": results})

    @action(detail=False, methods=["post"], url_path="analyze/all")
    def analyze_all(self, request):
        service = AnalyzeAllCamerasService()
        saved = service.run()
        return Response({"saved": saved})

    @action(detail=False, methods=["get"], url_path="cameras")
    def cameras(self, request):
        neighborhood_id = request.query_params.get("neighborhood_id")
        region_id = request.query_params.get("region_id")
        neighborhood_name = request.query_params.get("neighborhood")
        ordering_param = request.query_params.get("ordering", "description")

        qs = Camera.objects.select_related("neighborhood", "neighborhood__region").all()

        if neighborhood_id:
            try:
                nb_uuid = uuid.UUID(str(neighborhood_id))
                qs = qs.filter(neighborhood_id=nb_uuid)
            except (ValueError, AttributeError):
                return Response(
                    {"detail": "neighborhood_id inválido"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if region_id:
            try:
                rg_uuid = uuid.UUID(str(region_id))
                qs = qs.filter(neighborhood__region_id=rg_uuid)
            except (ValueError, AttributeError):
                return Response(
                    {"detail": "region_id inválido"}, status=status.HTTP_400_BAD_REQUEST
                )

        if neighborhood_name:
            qs = qs.filter(neighborhood__name__icontains=neighborhood_name)

        qs = self.apply_ordering(qs, ordering_param)

        paginator = DefaultPageNumberPagination()
        page_items = paginator.paginate_queryset(qs, request, view=self)

        data_out = []
        for cam in page_items:
            nb = cam.neighborhood
            rg = nb.region if nb else None
            data_out.append(
                {
                    "id": str(cam.id),
                    "description": cam.description,
                    "status": cam.get_status_display(),
                    "video_hls": cam.video_hls,
                    "video_embed": cam.video_embed,
                    "neighborhood": (
                        {"id": str(nb.id), "name": nb.name} if nb else None
                    ),
                    "region": ({"id": str(rg.id), "name": rg.name} if rg else None),
                    "latitude": cam.latitude,
                    "longitude": cam.longitude,
                }
            )

        return paginator.get_paginated_response(data_out)
