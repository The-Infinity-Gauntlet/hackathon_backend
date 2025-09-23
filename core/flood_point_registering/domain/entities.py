from dataclasses import dataclass
from datetime import datetime
from typing import Any, Optional


@dataclass
class Flood_Point_Register:
    """Domain entity for a flood point register.

    This mirrors the simplified persistence model:
    - region: id (int/uuid) of Region
    - neighborhood: id (int/uuid) of Neighborhood
    - possibility: float in [0,1]
    - created_at/finished_at: datetimes delimiting the effect window
    - props: arbitrary JSON (GeoJSON Feature expected by presentation layer)
    """

    id: Optional[int] = None
    city: Any = None
    neighborhood: Any = None
    possibility: float = 0.0
    created_at: Optional[datetime] = None
    finished_at: Optional[datetime] = None
    props: Any = None

    def flood_active(self, now: datetime) -> bool:
        if self.created_at is None or self.finished_at is None:
            return False
        return self.created_at <= now <= self.finished_at
