from abc import ABC, abstractmethod

class WeatherRepository(ABC):
    @abstractmethod
    def fillWeather(self, lat: float, lon: float, start: str, end: str):
        pass
    
    @abstractmethod
    def fillFutureWeather(self, lat: float, lon: float):
        pass

    @abstractmethod
    def fillElevation(self, lat: float, lon: float):
        pass

    @abstractmethod
    def fillAll(self, weather: list):
        pass