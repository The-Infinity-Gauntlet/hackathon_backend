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
        # Carregamento compatível: tenta state_dict (torch.load), depois weights_only=False,
        # e por fim TorchScript (torch.jit.load) para arquivos .pt/.pth zipados.
        model_from_script: torch.nn.Module | None = None
        ckpt: dict | None = None
        try:
            maybe = torch.load(str(self.checkpoint_path), map_location=self.device)
            if isinstance(maybe, dict) and "model_state_dict" in maybe:
                ckpt = maybe
            else:
                ckpt = {
                    "model_state_dict": maybe,
                    "config": {"model_name": "resnet50", "num_classes": 2},
                    "class_names": ["normal", "flooded"],
                }
        except Exception:
            try:
                maybe = torch.load(
                    str(self.checkpoint_path),
                    map_location=self.device,
                    weights_only=False,  # type: ignore[arg-type]
                )
                if isinstance(maybe, dict) and "model_state_dict" in maybe:
                    ckpt = maybe
                else:
                    ckpt = {
                        "model_state_dict": maybe,
                        "config": {"model_name": "resnet50", "num_classes": 2},
                        "class_names": ["normal", "flooded"],
                    }
            except Exception:
                # TorchScript
                model_from_script = torch.jit.load(
                    str(self.checkpoint_path), map_location=self.device
                )

        if model_from_script is not None:
            self.class_names = ["normal", "flooded"]
            self.model = model_from_script
            self.model.to(self.device)
            self.model.eval()
        elif ckpt is not None:
            config = ckpt.get("config", {"model_name": "resnet50", "num_classes": 2})
            self.class_names = ckpt.get(
                "class_names", ["normal", "flooded"]
            )  # index 0/1

            from core.flood_camera_monitoring.infra.machine_model.model import get_model  # type: ignore

            self.model = get_model(
                config.get("model_name", "resnet50"),
                num_classes=len(self.class_names),
                pretrained=False,
            )
            self.model.load_state_dict(ckpt["model_state_dict"])  # type: ignore[index]
            self.model.to(self.device)
            self.model.eval()
        else:
            raise RuntimeError(
                f"Não foi possível carregar o checkpoint em '{self.checkpoint_path}'. "
                "Esperado state_dict (torch.save) ou TorchScript (torch.jit.save)."
            )

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

        names = [
            str(c).lower() for c in getattr(self, "class_names", ["normal", "flooded"])
        ]
        # Mapear índices conhecidos
        try:
            i_norm = names.index("normal")
        except ValueError:
            i_norm = 0
        try:
            i_flood = names.index("flooded")
        except ValueError:
            i_flood = 1 if len(probs) > 1 else 0
        i_med = None
        if "medium" in names:
            try:
                i_med = names.index("medium")
            except ValueError:
                i_med = None

        # Extrai probabilidades brutas (softmax)
        p_normal = float(probs[i_norm]) if i_norm < len(probs) else 0.0
        p_flooded = float(probs[i_flood]) if i_flood < len(probs) else 0.0
        p_medium = (
            float(probs[i_med]) if (i_med is not None and i_med < len(probs)) else 0.0
        )

        # Converte para porcentagens e normaliza para somar exatamente 100
        pcts = [p_normal * 100.0, p_flooded * 100.0]
        if i_med is not None:
            pcts.append(p_medium * 100.0)
        total = sum(pcts)
        if total <= 0:
            # fallback seguro
            if i_med is None:
                pct_normal, pct_flooded = 50.0, 50.0
                pct_medium = 0.0
            else:
                pct_normal, pct_flooded, pct_medium = 33.34, 33.33, 33.33
        else:
            scale = 100.0 / total
            pcts = [v * scale for v in pcts]
            if i_med is None:
                pct_normal, pct_flooded = pcts
                pct_medium = 0.0
            else:
                pct_normal, pct_flooded, pct_medium = pcts

        # Classe predita e confiança coerente com a classe escolhida
        # Considera todas as classes disponíveis
        if i_med is None:
            values = [pct_normal, pct_flooded]
            idx = int(values.index(max(values)))
            pred_label = ["normal", "flooded"][idx]
        else:
            values = [pct_normal, pct_flooded, pct_medium]
            labels = ["normal", "flooded", "medium"]
            idx = int(values.index(max(values)))
            pred_label = labels[idx]

        is_flooded = pred_label == "flooded"
        confidence = float(values[idx])

        probabilities = FloodProbabilities(
            normal=pct_normal, flooded=pct_flooded, medium=pct_medium
        )
        return FloodAssessment(
            confidence=confidence, is_flooded=is_flooded, probabilities=probabilities
        )
