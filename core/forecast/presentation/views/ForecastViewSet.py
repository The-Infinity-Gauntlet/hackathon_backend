from rest_framework.viewsets import ModelViewSet
from core.forecast.infra.models import Forecast
from core.forecast.presentation.serializers.ForecastSerializer import ForecastSerializer

class ForecastViewSet(ModelViewSet):
    queryset = Forecast.objects.all()
    serializer_class = ForecastSerializer
    # Deixa o Forecast livre para um CRUD manual