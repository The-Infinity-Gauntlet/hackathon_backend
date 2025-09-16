from dataclasses import dataclass
from typing import Optional

from core.flood_camera_monitoring.application.dto.predict_request import (
    PredictRequest,
)
from core.flood_camera_monitoring.application.dto.predict_response import (
    PredictResponse,
)
from core.flood_camera_monitoring.domain.repository import FloodClassifierPort


@dataclass
class DetectFloodFromImage:
    """Caso de uso: detectar alagamento a partir de uma imagem.

    Depende apenas da porta de domínio (FloodClassifierPort), que é implementada
    por um adaptador na camada de infraestrutura.
    """

    classifier: FloodClassifierPort

    def execute(self, request: PredictRequest) -> PredictResponse:
        assessment = self.classifier.predict(request.image)
        return PredictResponse(
            is_flooded=assessment.is_flooded,
            severity=getattr(assessment, "severity", None),
            confidence=assessment.confidence,
            probabilities=assessment.probabilities,
            meta=request.meta,
        )
