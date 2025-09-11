class Forecast:
    def __init__(self, latitude: float, longitude: float, date: str, flood: int=None, probability: int=None):
        self.latitude = latitude
        self.longitude = longitude
        self.date = date
        self.flood = flood
        self.probability = probability