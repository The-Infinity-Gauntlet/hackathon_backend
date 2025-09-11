from rest_framework.viewsets import ModelViewSet
from core.flood_point_registering.infra.models import Flood_Point_Register
from core.flood_point_registering.presentation.serializers.RegisterSerializer import FloodPointRegisterSerializer

class FloodPointRegister(ModelViewSet):
    queryset = Flood_Point_Register.objects.all()
    serializer_class = FloodPointRegisterSerializer