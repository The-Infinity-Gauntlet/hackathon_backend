from core.flood_point_registering.domain.repository import RegisterRepository
from core.flood_point_registering.domain.entities import Flood_Point_Register
from typing import List
from datetime import timezone

class FloodPointRegisterService:
    def __init__(self, repository: RegisterRepository):
        self.repository = repository
    
    def registerFloodPoint(self, flood_point: Flood_Point_Register):
        return self.repository.saveRegister(flood_point)
    
    def getFloodPoint(self, id: int):
        return self.repository.getRegister(id)
    
    def listRegister(self) -> List[Flood_Point_Register]:
        return self.repository.listRegisters()
    
    def listActiveRegister(self) -> List[Flood_Point_Register]:
        registers = self.repository.listRegisters()
        now = timezone.now()
        return [
            register for register in registers if register.create_at <= now and register.finished_at >= now
        ]
    
    def updateRegister(self, flood_point: Flood_Point_Register):
        return self.repository.updateRegister(flood_point)
    
    def deleteRegister(self, id: int):
        flood_point = Flood_Point_Register(id=id)
        return self.repository.deleteRegister(flood_point)