from dataclasses import dataclass
import os
import time
from typing import Any, Dict, List

from core.flood_camera_monitoring.application.dto.predict_response import (
    PredictResponse,
)
from core.flood_camera_monitoring.infra.models import Camera
from core.flood_camera_monitoring.adapters.gateways.opencv_stream_adapter import (
    OpenCVVideoStream,
)
from core.flood_camera_monitoring.infra.torch_flood_classifier import (
    build_default_classifier,
)


@dataclass
class PredictAllCamerasService:
    """Compute predictions for all ACTIVE cameras and return them as a list.

    Does NOT persist results. Captures a few frames to stabilize prediction
    and aggregates probabilities.
    """

    sample_frames: int = int(os.getenv("FLOOD_SAMPLE_FRAMES", "3"))
    sample_interval_ms: int = int(os.getenv("FLOOD_SAMPLE_INTERVAL_MS", "150"))
    warmup_drops: int = int(os.getenv("FLOOD_WARMUP_DROPS", "2"))

    # thresholds (mirror analyze service)
    strong_min: float = float(os.getenv("FLOOD_STRONG_MIN", "60.0"))
    medium_min: float = float(os.getenv("FLOOD_MEDIUM_MIN", "25.0"))
    medium_max: float = float(os.getenv("FLOOD_MEDIUM_MAX", "60.0"))
    trend_min_delta: float = float(os.getenv("FLOOD_TREND_MIN_DELTA", "10.0"))
    min_medium_frames: int = int(os.getenv("FLOOD_MIN_MEDIUM_FRAMES", "2"))

    def run(self) -> List[Dict[str, Any]]:
        clf = build_default_classifier()
        results: List[Dict[str, Any]] = []

        for cam in Camera.objects.filter(status=Camera.CameraStatus.ACTIVE).iterator():
            stream = OpenCVVideoStream(cam.video_hls)
            frames: list[bytes] = []
            try:
                # Drop initial frames
                for _ in range(max(0, int(self.warmup_drops))):
                    _ = stream.grab()
                attempts = max(1, int(self.sample_frames))
                for i in range(attempts):
                    img_bytes = stream.grab()
                    if img_bytes:
                        frames.append(img_bytes)
                    if i < attempts - 1 and self.sample_interval_ms > 0:
                        time.sleep(self.sample_interval_ms / 1000.0)
            finally:
                stream.close()

            # If no frame, return N/A style result
            if not frames:
                results.append(
                    {
                        "camera": {
                            "id": getattr(cam, "id", None),
                            "description": getattr(cam, "description", None),
                            "video_url": getattr(cam, "video_url", None),
                        },
                        "is_flooded": False,
                        "confidence": 0.0,
                        "probabilities": {"normal": 0.0, "flooded": 0.0},
                        "meta": {"frames": 0, "note": "no-frame"},
                    }
                )
                continue

            assessments: list[PredictResponse] = []
            best_idx = 0
            best_flooded = -1.0
            flooded_series: list[float] = []
            for idx, fb in enumerate(frames):
                a = clf.predict(fb)
                assessments.append(a)
                flooded = float(a.probabilities.flooded)
                if flooded > best_flooded:
                    best_flooded = flooded
                    best_idx = idx
                flooded_series.append(flooded)

            mean_normal = sum(float(a.probabilities.normal) for a in assessments) / len(
                assessments
            )
            mean_flooded = sum(
                float(a.probabilities.flooded) for a in assessments
            ) / len(assessments)
            # medium pode não existir em modelos 2-classes; trata como 0.0
            try:
                mean_medium = sum(
                    float(a.probabilities.medium) for a in assessments
                ) / len(assessments)
            except Exception:
                mean_medium = 0.0
            # Garantir soma 100 entre 2 ou 3 classes
            total = mean_normal + mean_flooded + mean_medium
            if total > 0:
                mean_normal = (mean_normal / total) * 100.0
                mean_flooded = (mean_flooded / total) * 100.0
                mean_medium = 100.0 - (mean_normal + mean_flooded)

            decision_flooded = max(best_flooded, mean_flooded)
            chosen = assessments[best_idx]
            # Ajustar confiança para a classe dominante na decisão
            chosen_conf = float(
                mean_flooded
                if decision_flooded == mean_flooded
                else max(chosen.probabilities.flooded, chosen.probabilities.normal)
            )

            # Early-warning (medium)
            strong = decision_flooded >= float(self.strong_min)
            rising_trend = False
            if len(flooded_series) >= 2:
                rising_trend = (flooded_series[-1] - flooded_series[0]) >= float(
                    self.trend_min_delta
                )
            medium_band = (
                float(self.medium_min) <= mean_flooded < float(self.medium_max)
            )
            medium_frames = sum(
                1
                for v in flooded_series
                if float(self.medium_min) <= v < float(self.strong_min)
            )
            medium_flag = (not strong) and (
                medium_band
                or medium_frames >= int(self.min_medium_frames)
                or (rising_trend and flooded_series[-1] >= float(self.medium_min))
            )

            results.append(
                {
                    "camera": {
                        "id": getattr(cam, "id", None),
                        "description": getattr(cam, "description", None),
                        "video_url": getattr(cam, "video_url", None),
                    },
                    "is_flooded": bool(chosen.is_flooded),
                    "confidence": chosen_conf,
                    "medium": bool(medium_flag),
                    "probabilities": {
                        "normal": float(mean_normal),
                        "flooded": float(mean_flooded),
                        "medium": float(mean_medium),
                    },
                    "meta": {
                        "frames": len(assessments),
                        "best_flooded": float(best_flooded),
                        "decision_flooded": float(decision_flooded),
                        "trend": {
                            "series": flooded_series,
                            "rising": bool(rising_trend),
                        },
                    },
                }
            )

        return results
