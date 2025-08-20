from core.weather.domain.repository import WeatherRepository

class WeatherService: # Dita as ações do domínio
    def __init__(self, repository: WeatherRepository):
        self.repository = repository

    def execute(self, lat: float, lon: float, neighborhood: str, start: str, end: str):
        all = self.repository.fillAll(lat, lon, neighborhood, start, end) # Chama, do repositório, todos os dados
        return { # Retorna o dicionário com os dados
            "days": all["days"],
            "rain": all["rain"],
            "temperature": all["temp"],
            "humidity": all["humidity"],
            "pressure": all["pressure"],
            "elevation": all["elevation"]
        }