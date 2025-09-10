class Flood_Point_Register:
    def __init__(self, city_id: int, region_id: int, neighborhood: int, possibility: float, create_at: str, finished_at: str, props: str) -> None:
        self.city_id = city_id
        self.region_id = region_id
        self.neighborhood = neighborhood
        self.possibility = possibility
        self.create_at = create_at
        self.finished_at = finished_at
        self.props = props