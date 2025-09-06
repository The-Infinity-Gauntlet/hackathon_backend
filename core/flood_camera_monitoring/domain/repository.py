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
    def save(self, camera: Camera) -> Camera:
        raise NotImplementedError

    @abstractmethod
    def update(self) -> Optional[Camera]:
        raise NotImplementedError

    @abstractmethod
    def delete(self, camera_id: str) -> None:
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, camera_id: str) -> Optional[Camera]:
        raise NotImplementedError

    @abstractmethod
    def get_all(self) -> list[Camera]:
        raise NotImplementedError


class FloodClassifierPort(ABC):
    """Porta de domínio para classificador de alagamento."""

    @abstractmethod
    def predict(self, image: ImageInput) -> FloodAssessment:
        raise NotImplementedError


class VideoStreamPort(ABC):
    """Porta de domínio para leitura de frames de uma stream de vídeo."""

    @abstractmethod
    def grab(self) -> ImageInput | None:
        """Captura um frame atual como ImageInput (por exemplo, bytes JPEG).

        Retorna None se não for possível capturar no momento.
        """
        raise NotImplementedError

    @abstractmethod
    def is_open(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    def close(self) -> None:
        raise NotImplementedError
