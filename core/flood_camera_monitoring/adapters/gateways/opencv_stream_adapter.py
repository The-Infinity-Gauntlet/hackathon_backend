from __future__ import annotations

from dataclasses import dataclass
from typing import Optional
import cv2  # type: ignore

from core.flood_camera_monitoring.domain.repository import VideoStreamPort


@dataclass
class OpenCVVideoStream(VideoStreamPort):
    url: str
    backend: int = cv2.CAP_FFMPEG

    def __post_init__(self) -> None:
        self._cap = cv2.VideoCapture(self.url, self.backend)
        # Best-effort low latency settings
        self._cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
        self._cap.set(cv2.CAP_PROP_FPS, 10)

    def is_open(self) -> bool:
        return bool(self._cap.isOpened())

    def grab(self):
        if not self.is_open():
            return None
        ret, frame = self._cap.read()
        if not ret or frame is None:
            return None
        # Encode to JPEG bytes to comply with ImageInput (bytes OK)
        ok, buf = cv2.imencode(".jpg", frame)
        if not ok:
            return None
        return buf.tobytes()

    def close(self) -> None:
        try:
            self._cap.release()
        except Exception:
            pass
