
from dataclasses import dataclass
from typing import Optional, List
from core.flood_camera_monitoring.domain.entities import Camera
from core.flood_camera_monitoring.domain.repository import CameraRepository


@dataclass
class CamerasService:
	repo: CameraRepository

	def create(self, camera: Camera) -> Camera:
		return self.repo.save(camera)

	def update(self, camera: Camera) -> Optional[Camera]:
		return self.repo.update(camera)

	def delete(self, camera_id: str) -> None:
		self.repo.delete(camera_id)

	def get_by_id(self, camera_id: str) -> Optional[Camera]:
		return self.repo.get_by_id(camera_id)

	def list(self) -> List[Camera]:
		return self.repo.get_all()