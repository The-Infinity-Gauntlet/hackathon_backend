from __future__ import annotations

from dataclasses import dataclass
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from core.uploader.domain.ports import UploaderPort, UploadResult


@dataclass
class DjangoStorageUploader(UploaderPort):
    base_dir: str = "uploads"

    def upload(self, data: bytes, *, path: str, content_type: str | None = None) -> UploadResult:
        # Build full relative path: base_dir/path
        if self.base_dir:
            rel_path = f"{self.base_dir.rstrip('/')}/{path.lstrip('/')}"
        else:
            rel_path = path.lstrip("/")

        saved_path = default_storage.save(rel_path, ContentFile(data))
        url = default_storage.url(saved_path)
        size = default_storage.size(saved_path)
        return UploadResult(url=url, path=saved_path, size=size, content_type=content_type)
