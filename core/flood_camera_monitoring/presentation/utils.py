"""Presentation layer helpers for flood camera monitoring endpoints.

Keeps response building and threshold logic in one place to avoid duplication
across views.
"""

from __future__ import annotations

import os
from typing import Mapping, Any


def get_thresholds() -> tuple[float, float]:
    """Return (medium_min, strong_min) thresholds in percent.

    Defaults align with service logic: medium >=25% and <60%, strong >=60%.
    """
    medium_min = float(os.getenv("FLOOD_MEDIUM_MIN", "25.0"))
    strong_min = float(os.getenv("FLOOD_STRONG_MIN", "60.0"))
    return medium_min, strong_min


def compute_medium_flag(probabilities: Mapping[str, float]) -> bool:
    """Derive the 'medium' boolean based on probs and thresholds.

    - Consider 'medium' only if flooded is below strong_min
    - True when medium in [medium_min, strong_min)
    """
    medium_min, strong_min = get_thresholds()
    flooded = float(probabilities.get("flooded", 0.0))
    medium = float(probabilities.get("medium", 0.0))
    return (medium_min <= medium < strong_min) and (flooded < strong_min)


def build_prediction_payload(res: Any) -> dict[str, Any]:
    """Normalize PredictResponse into the API payload format used by views.

    Expected fields in `res`:
      - is_flooded: bool
      - confidence: float
      - probabilities: object or mapping with attributes/keys normal/flooded/medium
      - meta: optional mapping
    """
    # Support both dot-access (attrs) and dict-like access
    probs_obj = getattr(res, "probabilities", {})

    def _get(pname: str, default: float = 0.0) -> float:
        if isinstance(probs_obj, dict):
            return float(probs_obj.get(pname, default))
        return float(getattr(probs_obj, pname, default))

    probs = {
        "normal": _get("normal", 0.0),
        "flooded": _get("flooded", 0.0),
        "medium": _get("medium", 0.0),
    }

    payload = {
        "is_flooded": bool(getattr(res, "is_flooded", False)),
        "confidence": float(getattr(res, "confidence", 0.0)),
        # compatibility fields for clients that expect top-level copies
        "normal": probs["normal"],
        "prob_medium": probs["medium"],
        "medium": compute_medium_flag(probs),
        "probabilities": probs,
    }
    meta = getattr(res, "meta", None)
    if isinstance(meta, dict):
        payload["meta"] = meta
    return payload
