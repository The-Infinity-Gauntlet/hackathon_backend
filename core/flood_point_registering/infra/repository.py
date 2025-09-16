from core.flood_point_registering.domain.entities import Flood_Point_Register as DomainRegister
from core.flood_point_registering.infra.models import Flood_Point_Register as DjangoRegister
from typing import Optional, List

class RegisterRepoImpl:
    def saveRegister(self, flood_point: DomainRegister) -> Optional[DomainRegister]:
        flood_obj = DjangoRegister.objects.create(city=flood_point.city, region=flood_point.region, neighborhood=flood_point.neighborhood, possibility=flood_point.possibility, created_at=flood_point.created_at, finished_at=flood_point.finished_at, props=flood_point.props)
        return DomainRegister(flood_obj)
    
    def getRegister(self, flood_point_id: int) -> Optional[DomainRegister]:
        return DjangoRegister.objects.filter(id=flood_point_id).first()
    
    def listRegisters(self, flood_point: DomainRegister) -> List[DomainRegister]:
        floods_points = DjangoRegister.objects.all()
        return [DomainRegister(
            id=floods_points.id,
            city=floods_points.city,
            region=floods_points.region,
            neighborhood=floods_points.neighborhood,
            created_at=floods_points.created_at,
            updated_at=floods_points.updated_at,
            props=floods_points.props
        )]
    
    def updateRegister(self, flood_point: DomainRegister) -> Optional[DomainRegister]:
        register_obj = DjangoRegister.objects.get(id=flood_point.id)
        register_obj.city = flood_point.city
        register_obj.region = flood_point.region
        register_obj.neighborhood = flood_point.neighborhood
        register_obj.created_at = flood_point.created_at
        register_obj.updated_at = flood_point.updated_at
        register_obj.props = flood_point.props
        return flood_point
    
    def deleteRegister(self, flood_point_id: int) -> Optional[DomainRegister]:
        return DjangoRegister.objects.filter(id=flood_point_id).delete()