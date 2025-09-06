from dataclasses import dataclass, field
from typing import Any, Dict

from core.flood_camera_monitoring.domain.entities import ImageInput


@dataclass(frozen=True)
class PredictRequest:
	"""DTO de entrada para predição.

	image pode ser:
	- caminho (str/Path)
	- bytes (conteúdo da imagem)
	"""

	image: ImageInput
	meta: Dict[str, Any] = field(default_factory=dict)

