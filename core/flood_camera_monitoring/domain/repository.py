from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional

from core.flood_camera_monitoring.domain.entities import (
    Camera,
    FloodAssessment,
    ImageInput,
)


class CameraRepository(ABC):
    """Porta de repositório para entidades de câmera no domínio."""

    @abstractmethod
    def save(self, camera: Camera) -> Camera:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def delete(self, camera_id: str) -> None:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, camera_id: str) -> Optional[Camera]:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def active_monitoring(self, camera_id: str) -> str:  # pragma: no cover
        """Ativa o monitoramento de uma câmera (contrato específico do domínio)."""
        raise NotImplementedError

    @abstractmethod
    def stop_monitoring(self, camera_id: str) -> str:  # pragma: no cover
        """Ativa o monitoramento de uma câmera (contrato específico do domínio)."""
        raise NotImplementedError


class FloodClassifierPort(ABC):
    """Porta de domínio para classificador de alagamento."""

    @abstractmethod
    def predict(self, image: ImageInput) -> FloodAssessment:  # pragma: no cover
        raise NotImplementedError


class VideoStreamPort(ABC):
    """Porta de domínio para leitura de frames de uma stream de vídeo."""

    @abstractmethod
    def grab(self) -> ImageInput | None:  # pragma: no cover
        """Captura um frame atual como ImageInput (por exemplo, bytes JPEG).

        Retorna None se não for possível capturar no momento.
        """
        raise NotImplementedError

    @abstractmethod
    def is_open(self) -> bool:  # pragma: no cover
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:  # pragma: no cover
        raise NotImplementedError
