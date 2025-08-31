"""Infra wrapper exposing the Torch-based Flood Classifier.

This keeps backward compatibility for scripts importing from infra while the
implementation lives in adapters/gateways, following clean architecture.
"""
from pathlib import Path
from typing import Union

from core.flood_camera_monitoring.adapters.gateways.torch_classifier_adapter import (
    TorchFloodClassifier as TorchFloodClassifier,
)


def build_default_classifier(
    checkpoint_path: Union[str, Path] | None = None, device: str = "cpu"
) -> TorchFloodClassifier:
    if checkpoint_path is None:
        checkpoint_path = (
            Path(__file__).resolve().parent / "machine_model" / "best_real_model.pth"
        )
    return TorchFloodClassifier(str(checkpoint_path), device=device)
