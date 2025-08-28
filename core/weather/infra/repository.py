from core.weather.domain.repository import WeatherRepository
from core.weather.infra.models import Weather
from core.weather.infra.services.weather import fillClimate as fillClimateService, fillElevation, fillFutureClimate, fillFlood
import pandas as pd
from datetime import date, timedelta

hoje = date.today()
forecast_start = hoje - timedelta(days=3)
forecast_end = hoje + timedelta(days=7)

class WeatherRepositoryImpl(WeatherRepository):
    def fillAll(self, lat, lon, neighborhood, start, end):
        weather = self.fillWeather(lat, lon, start, end)
        future = self.fillFutureWeather(lat, lon)
        flood = self.fillFlood(lat, lon)
        elevation = self.fillElevation(lat, lon)
        climates = []

        for i in range(len(weather["days"])): # para cada dia
            climates.append(
                Weather(
                    date=weather["days"][i],
                    neighborhood=neighborhood,
                    latitude=lat,
                    longitude=lon,
                    rain=weather.get("rain", [None]*len(weather["days"]))[i] or 0, # se não tiver "rain", retorne None para cada dia
                    temperature=weather.get("temperature", [None]*len(weather["days"]))[i] or 0,
                    humidity=weather.get("humidity", [None]*len(weather["days"]))[i] or 0,
                    elevation=elevation.get("elevation"),
                    pressure=weather.get("pressure", [None]*len(weather["days"]))[i] or 0,
                    river_discharge=flood.get("river_discharge", [None]*len(weather["days"]))[i] if i < len(flood.get("river_discharge", [None]*len(weather["days"]))) else 0
                )
            )
        
        Weather.objects.bulk_create(climates, ignore_conflicts=True)

        return {
            "days": weather.get("days", []),
            "rain": weather.get("rain", []),
            "temp": weather.get("temperature", []),
            "humidity": weather.get("humidity", []),
            "pressure": weather.get("pressure", []),
            "elevation": elevation["elevation"],
            "river_discharge": flood["river_discharge"]
        }

    def fillWeather(self, lat, lon, start, end):
        return fillClimateService(lat, lon, start, end)
    
    def fillFutureWeather(self, lat, lon):
        return fillFutureClimate(lat, lon, forecast_start, forecast_end)
    
    def fillFlood(self, lat, lon):
        return fillFlood(lat, lon)

    def fillElevation(self, lat, lon):
        return fillElevation(lat, lon)