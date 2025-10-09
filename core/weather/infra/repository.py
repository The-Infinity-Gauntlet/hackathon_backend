from core.weather.domain.repository import WeatherRepository
from core.weather.infra.models import Weather
from core.weather.infra.services.weather import fillClimate as fillClimateService, fillElevation, fillFutureClimate, fillFlood
import pandas as pd
from datetime import date, timedelta, datetime

today = date.today()
forecast_start = today - timedelta(days=3)
forecast_end = today + timedelta(days=7)

class WeatherRepositoryImpl(WeatherRepository):
    def fillAll(self, lat, lon, neighborhood, start, end):
        if isinstance(start, str):
            start = datetime.strptime(start, "%Y-%m-%d").date()
        if isinstance(end, str):
            end = datetime.strptime(end, "%Y-%m-%d").date()
        end = end
        weather = self.fillWeather(lat, lon, start, today)
        future = self.fillFutureWeather(lat, lon)
        flood = self.fillFlood(lat, lon)
        elevation = self.fillElevation(lat, lon)
        climates = []

        all_days = weather["days"] + future["days"]
        for i, day in enumerate(all_days):
            if i < len(weather["days"]):
                source = weather
                idx = i
            else:
                source = future
                idx = i - len(weather["days"])

            def safe_get(arr, idx, default=0):
                if arr is None:
                    return default
                return arr[idx] if idx < len(arr) else default

            climates.append(
                Weather(
                    date=day,
                    neighborhood=neighborhood,
                    latitude=lat,
                    longitude=lon,
                    rain=safe_get(source.get("rain"), idx, safe_get(future.get("rain"), i)), # se não tiver "rain", retorne None para cada dia
                    temperature=safe_get(source.get("temperature"), idx, safe_get(future.get("temperature"), i)),
                    humidity=safe_get(source.get("humidity"), idx, safe_get(future.get("humidity"), i)),
                    elevation=elevation.get("elevation"),
                    pressure=safe_get(source.get("pressure"), idx, safe_get(future.get("pressure"), i)),
                    river_discharge=safe_get(flood.get("river_discharge"), idx)
                )
            )
        
        Weather.objects.bulk_create(climates, ignore_conflicts=True)

        return {
            "days": all_days,
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