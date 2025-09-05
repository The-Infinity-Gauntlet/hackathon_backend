class Occurrence:
    def __init__(self, date: str, situation: str, type: str, neighborhood: str):
        self.date = date
        self.situation = situation
        self.type = type
        self.neighborhood = neighborhood

        def __str__(self):
            return f'{self.situation} - {self.date} - {self.neighborhood}'