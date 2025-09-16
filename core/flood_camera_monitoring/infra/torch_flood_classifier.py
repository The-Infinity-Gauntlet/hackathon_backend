"""Infra wrapper exposing the Torch-based Flood Classifier.

This keeps backward compatibility for scripts importing from infra while the
implementation lives in adapters/gateways, following clean architecture.
"""

from pathlib import Path
from typing import Union
import os
import gdown

from core.flood_camera_monitoring.adapters.gateways.torch_classifier_adapter import (
    TorchFloodClassifier as TorchFloodClassifier,
)


def build_default_classifier(
    checkpoint_path: Union[str, Path] | None = None, device: str = "cpu"
) -> TorchFloodClassifier:
    """Create a TorchFloodClassifier ensuring a valid checkpoint exists.

    Resolution order for checkpoint path:
    1) Explicit argument
    2) ENV FLOOD_MODEL_PATH
    3) Default: <this_dir>/machine_model/best_real_model.pth

    If the file is missing or looks like a Git LFS pointer/tiny stub, we
    download the real checkpoint via gdown.
    """

    # Choose path from args, env or default
    if checkpoint_path is None:
        env_path = os.getenv("FLOOD_MODEL_PATH")
        if env_path:
            checkpoint_path = Path(env_path)
        else:
            checkpoint_path = (
                Path(__file__).resolve().parent
                / "machine_model"
                / "best_real_model.pth"
            )
    else:
        checkpoint_path = Path(str(checkpoint_path))

    # Ensure folder exists
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)

    def _looks_like_lfs_pointer(p: Path) -> bool:
        try:
            with p.open("rb") as fh:
                head = fh.read(256)
            return head.startswith(b"version https://git-lfs.github.com")
        except Exception:
            return False

    needs_download = False
    if not checkpoint_path.exists() or checkpoint_path.is_dir():
        needs_download = True
    else:
        try:
            size = checkpoint_path.stat().st_size
        except Exception:
            size = 0
        if _looks_like_lfs_pointer(checkpoint_path) or size < 1024 * 1024:  # <1MB
            needs_download = True

    if needs_download:
        # Prefer full URL from env; otherwise, build from Google Drive ID
        url = os.getenv(
            "FLOOD_MODEL_URL",
            None,
        )
        if not url:
            drive_id = os.getenv(
                "FLOOD_MODEL_DRIVE_ID",
                "1S7sy4Ug6ypF2yG03ZODsAcTTsgKQMt18",
            )
            url = f"https://drive.google.com/uc?export=download&id={drive_id}"
        try:
            if checkpoint_path.exists() and checkpoint_path.is_file():
                checkpoint_path.unlink()
        except Exception:
            pass
        # Download model
        gdown.download(url, str(checkpoint_path), quiet=False)

    return TorchFloodClassifier(str(checkpoint_path), device=device)
