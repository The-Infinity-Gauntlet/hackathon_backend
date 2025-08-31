from dataclasses import dataclass
from typing import Any, Dict

from core.flood_camera_monitoring.domain.entities import FloodProbabilities


@dataclass(frozen=True)
class PredictResponse:
    is_flooded: bool
    confidence: float
    probabilities: FloodProbabilities
    meta: Dict[str, Any]
