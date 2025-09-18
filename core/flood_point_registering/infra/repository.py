from core.flood_point_registering.domain.entities import (
    Flood_Point_Register as DomainRegister,
)
from core.flood_point_registering.infra.models import (
    Flood_Point_Register as DjangoRegister,
)
from typing import Optional, List


class RegisterRepoImpl:
    def saveRegister(self, flood_point: DomainRegister) -> Optional[DomainRegister]:
        obj = DjangoRegister.objects.create(
            region=flood_point.region,
            neighborhood=flood_point.neighborhood,
            possibility=flood_point.possibility,
            created_at=flood_point.created_at,
            finished_at=flood_point.finished_at,
            props=flood_point.props,
        )
        return DomainRegister(
            id=obj.id,
            region=obj.region_id,
            neighborhood=obj.neighborhood_id,
            possibility=obj.possibility,
            created_at=obj.created_at,
            finished_at=obj.finished_at,
            props=obj.props,
        )

    def getRegister(self, flood_point_id: int) -> Optional[DomainRegister]:
        obj = DjangoRegister.objects.filter(id=flood_point_id).first()
        if not obj:
            return None
        return DomainRegister(
            id=obj.id,
            region=obj.region_id,
            neighborhood=obj.neighborhood_id,
            possibility=obj.possibility,
            created_at=obj.created_at,
            finished_at=obj.finished_at,
            props=obj.props,
        )

    def listRegisters(self, flood_point: DomainRegister = None) -> List[DomainRegister]:
        result: List[DomainRegister] = []
        for obj in DjangoRegister.objects.all().iterator():
            result.append(
                DomainRegister(
                    id=obj.id,
                    region=obj.region_id,
                    neighborhood=obj.neighborhood_id,
                    possibility=obj.possibility,
                    created_at=obj.created_at,
                    finished_at=obj.finished_at,
                    props=obj.props,
                )
            )
        return result

    def updateRegister(self, flood_point: DomainRegister) -> Optional[DomainRegister]:
        obj = DjangoRegister.objects.get(id=flood_point.id)
        obj.region_id = flood_point.region
        obj.neighborhood_id = flood_point.neighborhood
        obj.possibility = flood_point.possibility
        obj.created_at = flood_point.created_at
        obj.finished_at = flood_point.finished_at
        obj.props = flood_point.props
        obj.save(
            update_fields=[
                "region_id",
                "neighborhood_id",
                "possibility",
                "created_at",
                "finished_at",
                "props",
            ]
        )
        return flood_point

    def deleteRegister(self, flood_point_id: int) -> None:
        DjangoRegister.objects.filter(id=flood_point_id).delete()
