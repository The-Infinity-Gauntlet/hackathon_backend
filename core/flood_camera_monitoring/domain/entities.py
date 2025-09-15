from dataclasses import dataclass
from typing import Union
from pathlib import Path
from enum import Enum


class CameraStatus(Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"
    OFFLINE = "OFFLINE"


class Camera:
    def __init__(
        self,
        id: str,
        status: Union[str, CameraStatus],
        video_url: str,
        description: str,
        address_id: str,
    ) -> None:
        self.id = id
        self.status: CameraStatus = self._coerce_status(status)
        self.video_url = video_url
        self.description = description
        self.address_id = address_id

    @staticmethod
    def _coerce_status(value: Union[str, CameraStatus]) -> CameraStatus:
        if isinstance(value, CameraStatus):
            return value
        if isinstance(value, str):
            upper = value.strip().upper()
            try:
                return CameraStatus[upper]
            except KeyError:
                for st in CameraStatus:
                    if st.value.upper() == upper:
                        return st
        raise ValueError(f"Invalid CameraStatus: {value}")

    def activate(self) -> None:
        self.status = CameraStatus.ACTIVE

    def deactivate(self) -> None:
        self.status = CameraStatus.INACTIVE

    def mark_offline(self) -> None:
        self.status = CameraStatus.OFFLINE


@dataclass(frozen=True)
class FloodProbabilities:
    """Probabilidades por classe no domínio.
    Valores esperados em 0.0..100.0 (percentual) para simplicidade.
    Pode incluir a classe intermediária 'medium' quando o modelo for 3-classes.
    """

    normal: float
    medium: float
    flooded: float
    medium: float


class FloodSeverity(Enum):
    NORMAL = "normal"
    MEDIUM = "medium"
    FLOODED = "flooded"


@dataclass(frozen=True)
class FloodAssessment:
    """Resultado essencial de uma avaliação de alagamento no domínio."""

    confidence: float  # 0..100
    is_flooded: bool
    severity: FloodSeverity
    probabilities: FloodProbabilities


# Tipo de entrada de imagem aceito no domínio sem depender de PIL
ImageInput = Union[bytes, str, Path]
