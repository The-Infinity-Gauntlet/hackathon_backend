from core.occurrences.domain.repository import OccurrenceRepository
from core.occurrences.domain.entities import Occurrence
from typing import Optional, List

class OccurrenceService:
    def __init__(self, repository: OccurrenceRepository):
        self.repository = repository

    def registerOccurrence(self, datetime: str, situation: str, type: str, neighborhood: str) -> Occurrence:
        occurrence = Occurrence(id=None, datetime=datetime, situation=situation, type=type, neighborhood=neighborhood)
        return self.repository.save(occurrence)
    
    def getOccurrenceById(self, id: int) -> Optional[Occurrence]:
        occurrence = Occurrence(id=id)
        return self.repository.getOccurrence(occurrence)
    
    def listOccurrence(self, datetime: Optional[str] = None, situation: Optional[str] = None, type: Optional[str] = None, neighborhood: Optional[str] = None) -> List[Occurrence]:
        occurence = Occurrence(id=None, datetime=datetime, situation=situation, type=type, neighborhood=neighborhood)
        return self.repository.list(occurence)
    
    def updateOccurrence(self, id: int, datetime: str, situation: str, type: str, neighborhood: str) -> Occurrence:
        occurrence = Occurrence(id=id, datetime=datetime, situation=situation, type=type, neighborhood=neighborhood)
        return self.repository.update(occurrence)
    
    def deleteOccurrence(self, id: int) -> Occurrence:
        occurence = Occurrence(id=id)
        return self.repository.delete(occurence)