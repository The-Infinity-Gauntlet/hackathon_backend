from celery import shared_task
from core.weather.app.services import WeatherService
from core.weather.infra.repository import WeatherRepositoryImpl

@shared_task
def fillWeather(lat, lon, neighborhood, start, end):
    service = WeatherService(repository=WeatherRepositoryImpl())
    result = service.execute(lat, lon, neighborhood, start, end)
    return result