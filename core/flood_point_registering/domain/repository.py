from abc import ABC, abstractmethod
from core.flood_point_registering.domain.entities import Flood_Point_Register
from typing import List, Optional

class RegisterRepository:
    @abstractmethod
    def saveRegister(self, register: Flood_Point_Register):
        pass

    @abstractmethod
    def getRegister(self, register_id: int) -> Optional[Flood_Point_Register]:
        pass

    @abstractmethod
    def listRegisters(self, register: Flood_Point_Register) -> List[Flood_Point_Register]:
        pass

    @abstractmethod
    def deleteRegister(self, register_id: int) -> None:
        pass

    @abstractmethod
    def updateRegister(self, register: Flood_Point_Register) -> Flood_Point_Register:
        pass