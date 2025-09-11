import time
from dataclasses import dataclass
from typing import Generator

from core.flood_camera_monitoring.application.dto.predict_response import (
    PredictResponse,
)
from core.flood_camera_monitoring.application.dto.stream_request import (
    StreamDetectRequest,
)
from core.flood_camera_monitoring.domain.repository import (
    FloodClassifierPort,
    VideoStreamPort,
)


@dataclass
class DetectFloodFromStream:
    classifier: FloodClassifierPort
    stream: VideoStreamPort

    def run(self, request: StreamDetectRequest) -> Generator[PredictResponse, None, None]:
        """Itera realizando predições em frames capturados periodicamente.

        Gera PredictResponse a cada iteração bem-sucedida de captura+classificação.
        """
        iterations = 0
        try:
            while self.stream.is_open():
                # Max loops guard
                if request.max_iterations is not None and iterations >= request.max_iterations:
                    break

                frame = self.stream.grab()
                if frame is not None:
                    assessment = self.classifier.predict(frame)
                    yield PredictResponse(
                        is_flooded=assessment.is_flooded,
                        confidence=assessment.confidence,
                        probabilities=assessment.probabilities,
                        meta={**request.meta, "iteration": iterations},
                    )
                    iterations += 1

                time.sleep(max(0.0, request.interval_seconds))
        finally:
            self.stream.close()
