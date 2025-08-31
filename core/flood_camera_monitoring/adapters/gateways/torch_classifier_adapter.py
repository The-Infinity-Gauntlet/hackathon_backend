from __future__ import annotations

"""Adapter: classificador de alagamentos baseado em PyTorch.

Implementa a porta de domínio FloodClassifierPort para integrar o modelo
treinado (checkpoint .pth) com a aplicação.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Tuple, Union

import io
import torch
import torch.nn.functional as F
import torchvision.transforms as T
from PIL import Image

from core.flood_camera_monitoring.domain.entities import (
    FloodAssessment,
    FloodProbabilities,
    ImageInput,
)
from core.flood_camera_monitoring.domain.repository import FloodClassifierPort


def _to_pil(image: ImageInput) -> Image.Image:
    if isinstance(image, (str, Path)):
        return Image.open(image).convert("RGB")
    if isinstance(image, (bytes, bytearray)):
        return Image.open(io.BytesIO(image)).convert("RGB")
    raise TypeError(f"Unsupported image input type: {type(image)}")


@dataclass
class TorchFloodClassifier(FloodClassifierPort):
    checkpoint_path: Union[str, Path]
    device: Union[str, torch.device] = "cpu"

    def __post_init__(self) -> None:
        self.device = torch.device(self.device)

        # Carrega checkpoint
        ckpt = torch.load(str(self.checkpoint_path), map_location=self.device)
        config = ckpt.get("config", {"model_name": "resnet50", "num_classes": 2})
        self.class_names = ckpt.get("class_names", ["normal", "flooded"])  # index 0/1

        # Importa fábrica de modelos a partir do módulo src existente
        # Evitar dependência circular com domínio.
        from core.flood_camera_monitoring.infra.machine_model.model import get_model  # type: ignore

        self.model = get_model(
            config.get("model_name", "resnet50"),
            num_classes=len(self.class_names),
            pretrained=False,
        )
        self.model.load_state_dict(ckpt["model_state_dict"])  # type: ignore[index]
        self.model.to(self.device)
        self.model.eval()

        self.transform = T.Compose(
            [
                T.Resize((224, 224)),
                T.ToTensor(),
                T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
            ]
        )

    @torch.inference_mode()
    def predict(self, image: ImageInput) -> FloodAssessment:
        pil = _to_pil(image)
        x = self.transform(pil).unsqueeze(0).to(self.device)
        logits = self.model(x)
        probs = F.softmax(logits, dim=1)[0].detach().cpu().numpy()

        # Assumimos ordem [normal, flooded]
        idx = int(probs.argmax())
        pred_class = self.class_names[idx]
        is_flooded = pred_class.lower() == "flooded"
        confidence = float(probs[idx] * 100.0)
        probabilities = FloodProbabilities(
            normal=float(probs[0] * 100.0), flooded=float(probs[1] * 100.0)
        )
        return FloodAssessment(
            confidence=confidence, is_flooded=is_flooded, probabilities=probabilities
        )
