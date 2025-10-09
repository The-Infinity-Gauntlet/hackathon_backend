from celery import shared_task
from core.weather.app.services import WeatherService
from core.weather.infra.repository import WeatherRepositoryImpl
from datetime import datetime

@shared_task
def fillWeather(lat, lon, neighborhood, start, end):
    start = datetime.strptime(start, "%Y-%m-%d").date() if isinstance(start, str) else start
    end = datetime.strptime(end, "%Y-%m-%d").date() if isinstance(end, str) else end
    service = WeatherService(repository=WeatherRepositoryImpl())
    result = service.execute(lat, lon, neighborhood, start, end)
    return result