from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from core.uploader.domain.ports import UploaderPort, UploadResult


@dataclass
class UploadBinaryService:
    uploader: UploaderPort

    def execute(self, *, data: bytes, path: str, content_type: Optional[str] = None) -> UploadResult:
        return self.uploader.upload(data, path=path, content_type=content_type)
