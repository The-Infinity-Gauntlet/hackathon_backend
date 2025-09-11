from django.db import models
from core.addressing.infra.models import Region, Neighborhood

class Flood_Point_Register(models.Model):
    class City(models.IntegerChoices):
        JOINVILLE = 1, "Joinville"
        ARAQUARI = 2, "Araquari"
    city = models.IntegerField(choices=City.choices, default=City.JOINVILLE)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.PROTECT)
    possibility = models.FloatField()
    created_at = models.DateTimeField()
    finished_at = models.DateTimeField()
    props = models.JSONField()

    def __str__(self):
        return f'{self.possibility} - {self.neighborhood}, {self.city}'