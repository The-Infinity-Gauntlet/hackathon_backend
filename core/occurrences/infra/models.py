from django.db import models
import os, geopandas as gpd

def get_neighborhood():
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname((os.path.abspath(__file__)))))
    file = os.path.join(BASE_DIR, "weather", "fixtures", "neighborhoods.geojson")
    choices = []
    neighborhoods = gpd.read_file(file)
    for _, nb in neighborhoods.iterrows():
        if "bairro" in nb:
            neighborhood = nb["bairro"]
            choices.append((neighborhood, neighborhood))
    return choices

class Occurrence(models.Model):
    date = models.DateField()
    class Situation(models.IntegerChoices):
        ALERTA = 1, "alerta"
        ATENCAO = 2, "atencao"
        MOBILIZACAO = 3, "mobilizacao"
        NORMALIDADE = 4, "normalidade"
    situation = models.IntegerField(choices=Situation.choices, default=Situation.NORMALIDADE)
    type = models.CharField(max_length=80)
    neighborhood = models.CharField(max_length=22, choices=get_neighborhood())

    def __str__(self):
        return f'{self.situation} - {self.date} - {self.neighborhood}'