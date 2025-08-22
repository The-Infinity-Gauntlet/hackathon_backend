from core.forecast.domain.repository import MachineLearningRepository
from core.weather.infra.models import Weather

class ForecastRepoImpl(MachineLearningRepository):
    def getCoords(self):
        return Weather.objects.values("latitude", "longitude").distinct()