class enviromentWeather:
    def __init__(self, date: str, latitude: float, longitude: float, neighborhood: str, rain: float | None, humidity: float | None, altitude: float | None, pressure: float | None):
        self.date = date
        self.latitude = latitude
        self.longitude = longitude
        self.neighborhood = neighborhood
        self.rain = rain
        self.humidity = humidity
        self.altitude = altitude
        self.pressure = pressure

    def __str__(self):
        return f"{self.date} - {self.latitude}, {self.longitude}"