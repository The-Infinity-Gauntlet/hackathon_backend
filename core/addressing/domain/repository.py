from typing import Protocol, Optional, Iterable
from .entities import Address, Region, Neighborhood


class AddressRepository(Protocol):
    def get_by_id(self, id: str) -> Optional[Address]:
        """Fetch a single address by its identifier or return None."""
        pass

    def find_by_neighborhood(
        self, neighborhood: str, city: Optional[str] = None
    ) -> Iterable[Address]:
        """Return addresses by neighborhood; optionally filter within a city."""
        pass

    def find_by_region_id(self, region_id: str) -> Iterable[Address]:
        """Return all addresses linked to a given region/area id."""
        pass

    def create_address(self, address: Address) -> Address:
        """Persist a new address; should fail if the id already exists."""
        pass

    def update_address(self, address: Address) -> Address:
        """Update an existing address; should fail if it doesn't exist."""
        pass

    def list_all(self) -> Iterable[Address]:
        """Return an iterable of all addresses (paged externally if needed)."""
        pass

    def find_by_city(self, city: str) -> Iterable[Address]:
        pass

    def find_by_neighborhood_id(self, neighborhood_id: str) -> Iterable[Address]:
        pass


class RegionRepository(Protocol):
    def get_by_id(self, id: str) -> Optional[Region]:
        pass

    def list_by_city(self, city: str) -> Iterable[Region]:
        pass

    def create_region(self, region: Region) -> Region:
        pass

    def update_region(self, region: Region) -> Region:
        pass


class NeighborhoodRepository(Protocol):
    def get_by_id(self, id: str) -> Optional[Neighborhood]:
        pass

    def list_by_city(self, city: str) -> Iterable[Neighborhood]:
        pass

    # Added to support GeoJSON feature collection service and Django impl
    def list_all(self) -> Iterable[Neighborhood]:
        """Return all neighborhoods."""
        pass

    def list_by_city_and_region(self, city: str, region: str) -> Iterable[Neighborhood]:
        """Return neighborhoods filtered by city and region name."""
        pass

    def create_neighborhood(self, neighborhood: Neighborhood) -> Neighborhood:
        pass

    def update_neighborhood(self, neighborhood: Neighborhood) -> Neighborhood:
        pass
