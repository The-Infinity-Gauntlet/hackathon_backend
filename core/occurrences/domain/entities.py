class Occurrence:
    def __init__(self, datetime: str, situation: str, type: str, neighborhood: str):
        self.datetime = datetime
        self.situation = situation
        self.type = type
        self.neighborhood = neighborhood

        def __str__(self):
            return f'{self.situation} - {self.datetime} - {self.neighborhood}'