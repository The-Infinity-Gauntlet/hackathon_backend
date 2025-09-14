from dataclasses import dataclass
import os
import time
from typing import Any, Dict, List

from core.flood_camera_monitoring.application.dto.predict_response import (
    PredictResponse,
)
from core.flood_camera_monitoring.infra.models import Camera
from core.flood_camera_monitoring.infra.torch_flood_classifier import (
    build_default_classifier,
)
from core.flood_camera_monitoring.application.utils.evaluation import (
    EvalConfig,
    capture_frames,
    aggregate_predictions,
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

        cfg = EvalConfig(
            sample_frames=self.sample_frames,
            sample_interval_ms=self.sample_interval_ms,
            warmup_drops=self.warmup_drops,
            strong_min=self.strong_min,
            medium_min=self.medium_min,
            medium_max=self.medium_max,
            trend_min_delta=self.trend_min_delta,
            min_medium_frames=self.min_medium_frames,
        )

        for cam in Camera.objects.filter(status=Camera.CameraStatus.ACTIVE).iterator():
            stream_url = getattr(cam, "video_hls", None)
            if not stream_url:
                results.append(
                    {
                        "camera": {
                            "id": getattr(cam, "id", None),
                            "description": getattr(cam, "description", None),
                        },
                        "is_flooded": False,
                        "confidence": 0.0,
                        "medium": False,
                        "probabilities": {"normal": 0.0, "flooded": 0.0, "medium": 0.0},
                        "meta": {"frames": 0, "note": "no-stream"},
                    }
                )
                continue
            frames = capture_frames(stream_url, cfg)

            # If no frame, return N/A style result
            if not frames:
                results.append(
                    {
                        "camera": {
                            "id": getattr(cam, "id", None),
                            "description": getattr(cam, "description", None),
                        },
                        "is_flooded": False,
                        "confidence": 0.0,
                        "medium": False,
                        "probabilities": {"normal": 0.0, "flooded": 0.0, "medium": 0.0},
                        "meta": {"frames": 0, "note": "no-frame"},
                    }
                )
                continue

            summary, assessments = aggregate_predictions(frames, clf, cfg)

            results.append(
                {
                    "camera": {
                        "id": getattr(cam, "id", None),
                        "description": getattr(cam, "description", None),
                    },
                    "is_flooded": bool(summary["strong"]),
                    "confidence": float(summary["chosen_confidence"]),
                    "medium": bool(summary["medium_flag"]),
                    "probabilities": {
                        "normal": float(summary["mean_normal"]),
                        "flooded": float(summary["mean_flooded"]),
                        "medium": float(summary["mean_medium"]),
                    },
                    "meta": {
                        "frames": int(summary["frames_count"]),
                        "best_flooded": float(summary["best_flooded"]),
                        "decision_flooded": float(summary["decision_flooded"]),
                        "trend": summary["trend"],
                    },
                }
            )

        return results
