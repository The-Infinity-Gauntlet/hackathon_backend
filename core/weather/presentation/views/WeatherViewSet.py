from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from core.weather.infra.models import Weather
from core.weather.presentation.serializers import WeatherSerializer
from core.weather.app.services import WeatherService
from core.weather.infra.repository import WeatherRepositoryImpl
from rest_framework.response import Response

class WeatherViewSet(ModelViewSet):
    queryset = Weather.objects.all()
    serializer_class = WeatherSerializer

    @action(detail=False, methods=["get"])
    def toFill(self, request):
        lat = float(request.query_params.get("lat"))
        lon = float(request.query_params.get("lon"))
        start = request.query_params.get("start")
        end = request.query_params.get("end")

        service = WeatherService(repository=WeatherRepositoryImpl()) # Escolhe qual caso de uso utilizar
        result = service.execute(lat, lon, start, end)

        return Response({"status": "Dados climáticos preenchidos com sucesso.", "dados": result})