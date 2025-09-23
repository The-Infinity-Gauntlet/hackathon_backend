from rest_framework.viewsets import ModelViewSet
from core.users.presentation.permissions import IsAdminOrReadOnly
from core.occurrences.infra.models import Occurrence
from core.occurrences.presentation.serializers.OccurrenceSerializer import (
    OccurrenceSerializer,
)


class OccurrenceViewSet(ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]
    queryset = Occurrence.objects.all()
    serializer_class = OccurrenceSerializer
