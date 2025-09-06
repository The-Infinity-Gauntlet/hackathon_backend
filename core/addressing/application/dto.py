from dataclasses import dataclass
from typing import Optional


@dataclass
class AddressDTO:
    id: str
    street: str
    number: Optional[str] = None
    neighborhood: Optional[str] = None
    city: str = ""
    state: Optional[str] = None
    country: str = "Brazil"
    zipcode: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None


@dataclass
class RegionDTO:
    id: str
    name: str
    city: str
    geometry: dict | None = None
    props: dict | None = None
    bbox_min_lon: float | None = None
    bbox_min_lat: float | None = None
    bbox_max_lon: float | None = None
    bbox_max_lat: float | None = None
