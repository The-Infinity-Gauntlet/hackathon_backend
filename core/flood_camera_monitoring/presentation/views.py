from core.flood_camera_monitoring.application.use_cases.analyze_all_cameras import (
    AnalyzeAllCamerasService,
)
from core.flood_camera_monitoring.application.use_cases.predict_all_cameras import (
    PredictAllCamerasService,
)
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.flood_camera_monitoring.presentation.serializers import (
    StreamSnapshotSerializer,
    StreamBatchSerializer,
)
from django.conf import settings
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
from core.flood_camera_monitoring.infra.models import Camera
from core.addressing.infra.models import Neighborhood, Region


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
                # Espelha normal e medium no topo para compatibilidade com PredictAll
                "normal": res.probabilities.normal,
                "prob_medium": getattr(res.probabilities, "medium", 0.0),
                # medium flag agora deriva da maior probabilidade entre medium e flooded abaixo de strong threshold
                "medium": bool(
                    getattr(res.probabilities, "medium", 0.0) >= 25.0
                    and getattr(res.probabilities, "medium", 0.0) < 60.0
                    and res.probabilities.flooded < 60.0
                ),
                "probabilities": {
                    "normal": res.probabilities.normal,
                    "flooded": res.probabilities.flooded,
                    "medium": getattr(res.probabilities, "medium", 0.0),
                },
                "camera_install_url": getattr(settings, "CAMERA_INSTALL_URL", ""),
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
                    "normal": res.probabilities.normal,
                    "prob_medium": getattr(res.probabilities, "medium", 0.0),
                    # medium flag baseada na probabilidade medium direta
                    "medium": bool(
                        getattr(res.probabilities, "medium", 0.0) >= 25.0
                        and getattr(res.probabilities, "medium", 0.0) < 60.0
                        and res.probabilities.flooded < 60.0
                    ),
                    "probabilities": {
                        "normal": res.probabilities.normal,
                        "flooded": res.probabilities.flooded,
                        "medium": getattr(res.probabilities, "medium", 0.0),
                    },
                    "meta": res.meta,
                }
            )

        return Response(
            {
                "results": results,
                "camera_install_url": getattr(settings, "CAMERA_INSTALL_URL", ""),
            }
        )


class AnalyzeAllCamerasView(APIView):
    """HTTP endpoint para disparar a análise de todas as câmeras ativas.

    Retorna o número de registros salvos (confidence < 60%).
    """

    def post(self, request, *args, **kwargs):
        service = AnalyzeAllCamerasService()
        saved = service.run()
        return Response(
            {
                "saved": saved,
                "camera_install_url": getattr(settings, "CAMERA_INSTALL_URL", ""),
            }
        )


class PredictAllCamerasView(APIView):
    """HTTP endpoint para retornar a predição de todas as câmeras ativas.

    Não persiste nada; retorna lista com probabilidades (inclui 'normal').
    """

    def get(self, request, *args, **kwargs):
        service = PredictAllCamerasService()
        data = service.run()
        # espelhar o campo "normal" também no topo de cada item
        for item in data:
            item["normal"] = float(item.get("probabilities", {}).get("normal", 0.0))
            # também espelha a probabilidade de medium no topo para facilitar filtros/monitoramento
            item["prob_medium"] = float(
                item.get("probabilities", {}).get("medium", 0.0)
            )
        return Response(
            {
                "results": data,
                "camera_install_url": getattr(settings, "CAMERA_INSTALL_URL", ""),
            }
        )


class CamerasListView(APIView):
    """Lista todas as câmeras com possibilidade de filtro por bairro (neighborhood_id) ou região (region_id).
    Parâmetros de query:
      - neighborhood_id: UUID de Neighborhood
      - region_id: UUID de Region (retorna câmeras cujos endereços pertencem a bairros dessa região)
    Ambos podem ser combinados; se ambos presentes, aplica interseção.
    """

    def get(self, request, *args, **kwargs):
        # Address FK removed; filtering now by simple text neighborhood if provided
        neighborhood_name = request.query_params.get("neighborhood")
        qs = Camera.objects.all()
        if neighborhood_name:
            qs = qs.filter(neighborhood__icontains=neighborhood_name)

        data = []
        for cam in qs.iterator():
            data.append(
                {
                    "id": str(cam.id),
                    "description": cam.description,
                    "status": cam.get_status_display(),
                    "video_hls": cam.video_hls,
                    "video_embed": cam.video_embed,
                    "neighborhood": cam.neighborhood,
                    "latitude": cam.latitude,
                    "longitude": cam.longitude,
                }
            )
        return Response(
            {
                "results": data,
                "count": len(data),
                "camera_install_url": getattr(settings, "CAMERA_INSTALL_URL", ""),
            }
        )
