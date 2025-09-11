from .dto import AddressDTO, RegionDTO
from dataclasses import dataclass
from core.addressing.domain.entities import Region
from core.addressing.domain.repository import RegionRepository


def format_address_line(a: AddressDTO) -> str:
    parts = [a.street]
    if a.number:
        parts.append(a.number)
    if a.neighborhood:
        parts.append(a.neighborhood)
    city_state = " / ".join(filter(None, [a.city, a.state]))
    if city_state:
        parts.append(city_state)
    if a.zipcode:
        parts.append(a.zipcode)
    if a.country:
        parts.append(a.country)
    return ", ".join(parts)


@dataclass
class RegionService:
    repo: RegionRepository

    def create(self, dto: RegionDTO) -> Region:
        if not dto.name or not dto.city:
            raise ValueError("name and city are required")
        region = Region(
            id=dto.id,
            name=dto.name,
            city=dto.city,
            props=dto.props or None,
            geometry=dto.geometry or None,
            bbox_min_lon=dto.bbox_min_lon,
            bbox_min_lat=dto.bbox_min_lat,
            bbox_max_lon=dto.bbox_max_lon,
            bbox_max_lat=dto.bbox_max_lat,
        )
        return self.repo.create_region(region)
