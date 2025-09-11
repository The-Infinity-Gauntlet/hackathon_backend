import time
from dataclasses import dataclass

from core.flood_camera_monitoring.application.dto.predict_response import PredictResponse
from core.flood_camera_monitoring.application.dto.snapshot_request import (
    SnapshotDetectRequest,
)
from core.flood_camera_monitoring.domain.repository import (
    FloodClassifierPort,
    VideoStreamPort,
)


@dataclass
class DetectFloodSnapshotFromStream:
    classifier: FloodClassifierPort
    stream: VideoStreamPort

    def execute(self, request: SnapshotDetectRequest) -> PredictResponse:
        deadline = time.time() + float(request.timeout_seconds)
        try:
            while self.stream.is_open() and time.time() < deadline:
                img = self.stream.grab()
                if img is not None:
                    assessment = self.classifier.predict(img)
                    return PredictResponse(
                        is_flooded=assessment.is_flooded,
                        confidence=assessment.confidence,
                        probabilities=assessment.probabilities,
                        meta=request.meta,
                    )
                # Tiny sleep to avoid busy loop
                time.sleep(0.05)
        finally:
            self.stream.close()

        # Could not capture a frame in time
        raise TimeoutError("Could not capture frame before timeout")
