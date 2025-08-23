from core.occurrences.domain.repository import OccurrenceRepository
from core.occurrences.domain.entities import Occurrence as DomainOccurrence
from core.occurrences.infra.models import Occurrence as DjangoOccurrence
from typing import Optional

class OccurrenceRepoImpl(OccurrenceRepository):
    def save(self, occurrence: DomainOccurrence) -> Optional[DomainOccurrence]:
        occurrence_obj = DjangoOccurrence.objects.create(date=occurrence.date, situation=occurrence.situation, type=occurrence.type, neighborhood=occurrence.neighborhood)
        return DomainOccurrence(id=occurrence_obj.id, date=occurrence_obj.date, situation=occurrence_obj.situation, type=occurrence_obj.type, neighborhood=occurrence_obj.neighborhood)
    
    def getOccurrence(self, occurrence_id: int) -> Optional[DomainOccurrence]:
        return DjangoOccurrence.objects.filter(id=occurrence_id).first()
    
    def list(self, occurrence: DomainOccurrence):
        occurrences = DjangoOccurrence.objects.all()
        return [DomainOccurrence(
                id=occurrences.id,
                date=occurrences.date,
                situation=occurrences.situation,
                type=occurrences.type,
                neighborhood=occurrences.neighborhoods
            )]
    
    def delete(self, occurrence_id: int) -> None:
        return DjangoOccurrence.objects.filter(id=occurrence_id).delete()
    
    def update(self, occurrence) -> DomainOccurrence:
        occurrence_obj = DjangoOccurrence.objects.get(id=occurrence.id)
        occurrence_obj.date = occurrence.date
        occurrence_obj.situation = occurrence.situation
        occurrence_obj.type = occurrence.type
        occurrence_obj.neighborhood = occurrence.neighborhood
        occurrence_obj.save()
        return occurrence