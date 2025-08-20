from core.weather.domain.repository import WeatherRepository
from core.weather.infra.services.weather import fillClimate as fillClimateService, fillElevation, fillFutureClimate
import pandas as pd

class WeatherRepositoryImpl(WeatherRepository):
    def fillAll(self, lat, lon, neighborhood, start, end):
        weather = self.fillWeather(lat, lon, start, end)
        future = self.fillFutureWeather(lat, lon, start, end)
        elevation = self.fillElevation(lat, lon)

        records = []
        for i in range(len(weather["days"])): # para cada dia
            records.append({
                "date": weather["days"][i],
                "latitude": lat,
                "longitude": lon,
                "neighborhood": neighborhood,
                "rain": weather.get("rain", [None]*len(weather["days"])), # se não tiver "rain", retorne None para cada dia
                "humidity": weather.get("humidity", [None]*len(weather["days"])),
                "elevation": elevation.get("elevation", [None]*len(weather["days"])),
                "pressure": weather.get("pressure", [None]*len(weather["days"]))[i]
            })

        df = pd.DataFrame(records)
        df.to_parquet(f'clima_{neighborhood}_{start}_{end}')

    def fill_climate(self, lat, lon, start, end):
        return fillClimateService(lat, lon, start, end)
    
    def fill_future_climate(self, lat, lon, start, end):
        return fillFutureClimate(lat, lon, start, end)

    def fill_elevation(self, lat, lon):
        return fillElevation(lat, lon)