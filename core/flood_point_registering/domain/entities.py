import datetime

class Flood_Point_Register:
    def __init__(self, city: int, region_id: int, neighborhood: int, possibility: float, create_at: datetime, finished_at: datetime, props: str) -> None:
        self.city = city
        self.region_id = region_id
        self.neighborhood = neighborhood
        self.possibility = possibility
        self.created_at = create_at
        self.finished_at = finished_at
        self.props = props

    def flood_active(self, now: datetime) -> bool:
        return self.create_at <= now <= self.finished_at