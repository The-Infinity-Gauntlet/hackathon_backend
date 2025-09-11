from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass(frozen=True)
class SnapshotDetectRequest:
    timeout_seconds: float = 5.0
    meta: Dict[str, Any] = field(default_factory=dict)
