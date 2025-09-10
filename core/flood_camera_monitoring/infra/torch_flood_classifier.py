"""Infra wrapper exposing the Torch-based Flood Classifier.

This keeps backward compatibility for scripts importing from infra while the
implementation lives in adapters/gateways, following clean architecture.
"""

from pathlib import Path
import os
from typing import Union

from core.flood_camera_monitoring.adapters.gateways.torch_classifier_adapter import (
    TorchFloodClassifier as TorchFloodClassifier,
)


def build_default_classifier(
    checkpoint_path: Union[str, Path] | None = None, device: str = "cpu"
) -> TorchFloodClassifier:
    # 1) Permite override por variável de ambiente (ex.: colocar modelo em /app/media)
    env_path = os.getenv("FLOOD_MODEL_PATH")
    if env_path:
        return TorchFloodClassifier(env_path, device=device)

    # 2) Usa o parâmetro explícito, se fornecido
    if checkpoint_path is not None:
        return TorchFloodClassifier(str(checkpoint_path), device=device)

    # 3) Padrão: arquivo dentro do repositório (pode ser pointer LFS)
    default_path = (
        Path(__file__).resolve().parent / "machine_model" / "best_real_model.pth"
    )
    return TorchFloodClassifier(str(default_path), device=device)
