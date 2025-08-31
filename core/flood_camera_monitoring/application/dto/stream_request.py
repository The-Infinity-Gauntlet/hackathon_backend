from dataclasses import dataclass, field
from typing import Any, Dict, Optional


@dataclass(frozen=True)
class StreamDetectRequest:
    stream_url: str
    interval_seconds: float = 5.0
    max_iterations: Optional[int] = None  # None = infinito
    meta: Dict[str, Any] = field(default_factory=dict)
