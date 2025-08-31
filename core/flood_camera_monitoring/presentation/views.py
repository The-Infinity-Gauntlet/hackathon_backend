from core.flood_camera_monitoring.application.use_cases.analyze_all_cameras import (
    AnalyzeAllCamerasService,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.flood_camera_monitoring.presentation.serializers import (
    StreamSnapshotSerializer,
    StreamBatchSerializer,
)
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
from core.flood_camera_monitoring.application.dto.snapshot_request import (
    SnapshotDetectRequest,
)


class StreamSnapshotDetectView(APIView):
    """HTTP endpoint: pega 1 frame da stream e retorna a predição."""

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

        return Response(
            {
                "is_flooded": res.is_flooded,
                "confidence": res.confidence,
                "probabilities": {
                    "normal": res.probabilities.normal,
                    "flooded": res.probabilities.flooded,
                },
            }
        )


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

        results = []
        for res in service.run(req):
            results.append(
                {
                    "is_flooded": res.is_flooded,
                    "confidence": res.confidence,
                    "probabilities": {
                        "normal": res.probabilities.normal,
                        "flooded": res.probabilities.flooded,
                    },
                    "meta": res.meta,
                }
            )

        return Response({"results": results})


class AnalyzeAllCamerasView(APIView):
    """HTTP endpoint para disparar a análise de todas as câmeras ativas.

    Retorna o número de registros salvos (confidence < 60%).
    """

    def post(self, request, *args, **kwargs):
        service = AnalyzeAllCamerasService()
        saved = service.run()
        return Response({"saved": saved})
