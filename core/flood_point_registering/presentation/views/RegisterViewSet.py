from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from core.flood_point_registering.infra.models import Flood_Point_Register
from core.flood_point_registering.presentation.serializers.RegisterSerializer import (
    FloodPointRegisterSerializer,
)


class FloodPointRegister(ModelViewSet):
    queryset = Flood_Point_Register.objects.all()
    serializer_class = FloodPointRegisterSerializer

    @action(detail=False, methods=["get"], url_path="active")
    def active(self, request):
        now = timezone.now()
        qs = self.get_queryset().filter(created_at__lte=now, finished_at__gte=now)
        page = self.paginate_queryset(qs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data)
