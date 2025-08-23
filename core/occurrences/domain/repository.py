from abc import ABC, abstractmethod
from typing import List, Optional
from core.occurrences.domain.entities import Occurrence

class OccurrenceRepository(ABC):
    @abstractmethod
    def save(self, occurrence: Occurrence) -> Occurrence:
        pass

    def getOccurrence(self, occurrence_id: int) -> Optional[Occurrence]:
        pass

    @abstractmethod
    def list(self, occurrence: Occurrence) -> List[Occurrence]:
        pass

    @abstractmethod
    def delete(self, occurrence_id: int) -> None:
        pass

    @abstractmethod
    def update(self, occurrence: Occurrence) -> Occurrence:
        pass