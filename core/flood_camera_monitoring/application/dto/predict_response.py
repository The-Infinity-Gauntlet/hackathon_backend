from dataclasses import dataclass
from typing import Any, Dict

from core.flood_camera_monitoring.domain.entities import (
    FloodProbabilities,
    FloodSeverity,
)


@dataclass(frozen=True)
class PredictResponse:
    is_flooded: bool
    severity: FloodSeverity
    confidence: float
    probabilities: FloodProbabilities
    meta: Dict[str, Any]
    # Campo redundante para acesso direto à probabilidade de "normal" quando útil
    # Mantido para facilitar consumo no front e cumprir requisito explícito
    @property
    def normal(self) -> float:  # percentual 0..100
        return float(self.probabilities.normal)

    # Acesso direto à probabilidade da classe intermediária "medium"
    @property
    def medium(self) -> float:  # percentual 0..100
        return float(self.probabilities.medium)
