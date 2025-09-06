from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping, Optional


@dataclass(frozen=True)
class UploadResult:
    url: str
    path: str
    size: int
    content_type: Optional[str] = None
    meta: Mapping[str, str] | None = None


class UploaderPort:
    """Porta genérica para upload de arquivos (bytes)."""

    def upload(self, data: bytes, *, path: str, content_type: str | None = None) -> UploadResult:  # pragma: no cover
        raise NotImplementedError
