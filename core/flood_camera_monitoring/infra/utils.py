from __future__ import annotations

from pathlib import Path
import os


def resolve_checkpoint_path(env_var: str = "FLOOD_MODEL_PATH") -> Path:
    """Return checkpoint path from env or default location in infra/machine_model.

    Default: core/flood_camera_monitoring/infra/machine_model/best_real_model.pth
    """
    env_path = os.getenv(env_var)
    if env_path:
        return Path(env_path)
    return Path(__file__).resolve().parent / "machine_model" / "best_real_model.pth"


def looks_like_lfs_pointer(p: Path) -> bool:
    """Detect Git LFS pointer files to avoid treating them as real checkpoints."""
    try:
        if not p.exists() or not p.is_file():
            return False
        with p.open("rb") as fh:
            head = fh.read(256)
        return head.startswith(b"version https://git-lfs.github.com")
    except Exception:
        return False
