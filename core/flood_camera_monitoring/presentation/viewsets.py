from rest_framework import status, viewsets
from rest_framework.views import APIView
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
from django.http import Http404
import time
import subprocess
import shlex


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

    def post(self, request, *args, **kwargs):
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


class StreamBatchDetectView(APIView):
    """HTTP endpoint: executa N iterações rápidas e retorna a lista de resultados."""

    def post(self, request, *args, **kwargs):
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

        return Response(
            {
                "results": results,
            }
        )


# =====================
# HLS live loop helpers
# =====================


def _media_loop_url() -> str | None:
    root = Path(settings.MEDIA_ROOT)
    files = sorted([p.name for p in root.glob("*.mp4")])
    if not files:
        return None
    items = [f"media:{name}" for name in files]
    return "loop:" + ",".join(items)


def _ensure_dir(p: Path) -> None:
    p.mkdir(parents=True, exist_ok=True)


def _is_process_alive(pid: int) -> bool:
    try:
        os.kill(pid, 0)
        return True
    except Exception:
        return False


def _ensure_hls_live_loop() -> tuple[bool, str | None, str | None]:
    """Ensure an ffmpeg process is producing a looping HLS stream from media/*.mp4.

    Returns (ok, playlist_path, error).
    - playlist_path is absolute filesystem path to playlist.m3u8 (not URL)
    """
    media_root = Path(settings.MEDIA_ROOT)
    src_files = sorted([p for p in media_root.glob("*.mp4")])
    if not src_files:
        return False, None, "No .mp4 files in MEDIA_ROOT"

    out_dir = media_root / "hls" / "live"
    _ensure_dir(out_dir)
    concat_list = out_dir / "list.txt"
    source_mp4 = out_dir / "source.mp4"
    playlist = out_dir / "playlist.m3u8"
    pid_file = out_dir / "ffmpeg.pid"

    # 1) Build concat list for joining
    try:
        with concat_list.open("w", encoding="utf-8") as fh:
            for p in src_files:
                fh.write(f"file '{p.as_posix()}'\n")
    except Exception as e:
        return False, None, f"Failed to write concat list: {e}"

    # 2) If no source.mp4, build by concatenating (stream copy if possible)
    if not source_mp4.exists():
        cmd_copy = f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(concat_list))} -c copy {shlex.quote(str(source_mp4))}"
        try:
            subprocess.run(
                cmd_copy,
                shell=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except subprocess.CalledProcessError:
            # Fallback: re-encode to a uniform source
            cmd_encode = (
                f"ffmpeg -y -f concat -safe 0 -i {shlex.quote(str(concat_list))} "
                f"-c:v libx264 -preset veryfast -c:a aac {shlex.quote(str(source_mp4))}"
            )
            try:
                subprocess.run(
                    cmd_encode,
                    shell=True,
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except subprocess.CalledProcessError as e:
                return False, None, f"Failed to build source.mp4: {e}"

    # 3) Ensure ffmpeg HLS process running
    if pid_file.exists():
        try:
            pid = int(pid_file.read_text().strip())
        except Exception:
            pid = -1
        if pid > 0 and _is_process_alive(pid):
            return True, str(playlist), None
        # stale pid file: remove
        try:
            pid_file.unlink(missing_ok=True)  # type: ignore[arg-type]
        except Exception:
            pass

    # Start process
    seg_pattern = out_dir / "seg_%05d.ts"
    cmd_hls = (
        f"ffmpeg -loglevel warning -nostdin -re -stream_loop -1 -i {shlex.quote(str(source_mp4))} "
        f"-c:v libx264 -preset veryfast -g 48 -sc_threshold 0 -c:a aac -ar 44100 -b:a 128k "
        f"-f hls -hls_time 4 -hls_list_size 6 -hls_flags delete_segments+append_list+independent_segments "
        f"-hls_segment_filename {shlex.quote(str(seg_pattern))} {shlex.quote(str(playlist))}"
    )
    try:
        proc = subprocess.Popen(  # noqa: S603
            cmd_hls,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            preexec_fn=os.setsid,  # allow killing the whole group later
        )
        pid_file.write_text(str(proc.pid))
        # Give it a moment to start writing
        time.sleep(0.5)
        return True, str(playlist), None
    except Exception as e:
        return False, None, f"Failed to start ffmpeg: {e}"


# Simple rotating counter to avoid always sampling the very first frame
_predict_skip_counter = 0


def _next_skip_count() -> int:
    global _predict_skip_counter
    _predict_skip_counter = (_predict_skip_counter + 1) % 60  # cycle 0..59
    base = int(os.getenv("DEMO_PREDICT_SKIP_BASE", "5"))
    # Skip between base..base+counter, bounded to a reasonable max
    return min(base + _predict_skip_counter, 90)


class HealthcheckView(APIView):
    """Health endpoint: verifica modelo, DB e Redis.

    - Modelo baixado: checa existência e tamanho do checkpoint e evita LFS pointer
    - DB OK: abre um cursor e executa um SELECT 1
    - Redis OK: ping no broker configurado (CELERY_BROKER_URL)
    """

    def get(self, request, *args, **kwargs):
        # 1) Modelo
        env_path = os.getenv("FLOOD_MODEL_PATH")
        if env_path:
            checkpoint_path = Path(env_path)
        else:
            # Match the default used in build_default_classifier():
            # core/flood_camera_monitoring/infra/machine_model/best_real_model.pth
            checkpoint_path = (
                Path(__file__).resolve().parents[1]
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


class AnalyzeAllCamerasView(APIView):
    """HTTP endpoint para disparar a análise de todas as câmeras ativas.

    Retorna o número de registros salvos (confidence < 60%).
    """

    def post(self, request, *args, **kwargs):
        service = AnalyzeAllCamerasService()
        saved = service.run()
        return Response({"saved": saved}, status=status.HTTP_200_OK)

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

        # DRF pagination for consistency with other list endpoints
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

        # get_paginated_response will include count/next/previous and ordering
        return paginator.get_paginated_response(data_out)


class HlsLoopInfoView(APIView):
    """Return the HLS live loop URL and ensure the stream is running."""

    def get(self, request, *args, **kwargs):
        ok, playlist_path, err = _ensure_hls_live_loop()
        if not ok or not playlist_path:
            return Response({"ok": False, "error": err or "unknown"}, status=503)
        # Build public URL under MEDIA_URL
        rel = Path(playlist_path).relative_to(Path(settings.MEDIA_ROOT)).as_posix()
        hls_url = request.build_absolute_uri(
            (str(settings.MEDIA_URL).rstrip("/") + "/" + rel)
        )
        return Response({"ok": True, "hls_url": hls_url})


## Removed MJPEG and MP4 demo endpoints to simplify


class HlsPredictView(APIView):
    """Return a snapshot prediction for the demo HLS loop source (from media files)."""

    def get(self, request, *args, **kwargs):
        # Use the same source as HLS (loop of media files)
        loop_url = _media_loop_url()
        if not loop_url:
            raise Http404("No .mp4 files found in MEDIA_ROOT")

        clf = build_default_classifier()
        stream = OpenCVVideoStream(loop_url)
        # Advance a few frames to avoid sampling always the very first frame
        try:
            to_skip = _next_skip_count()
            for _ in range(max(0, to_skip)):
                _ = stream.grab()
                time.sleep(0.005)
        except Exception:
            pass
        service = DetectFloodSnapshotFromStream(classifier=clf, stream=stream)
        try:
            res = service.execute(
                SnapshotDetectRequest(
                    timeout_seconds=float(request.query_params.get("timeout", 5.0)),
                    meta={
                        "skipped_frames": int(to_skip) if "to_skip" in locals() else 0,
                        "source": loop_url,
                        "model_fallback": bool(getattr(clf, "_fallback", False)),
                        "checkpoint": str(getattr(clf, "checkpoint_path", "")),
                    },
                )
            )
        except TimeoutError:
            return Response({"detail": "Could not capture frame"}, status=504)

        return Response(build_prediction_payload(res))
