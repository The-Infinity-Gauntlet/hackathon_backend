from django.db import models

class Weather(models.Model):
    date = models.DateField()
    latitude = models.FloatField()
    longitude = models.FloatField()
    neighborhood = models.CharField()
    rain = models.FloatField(null=True)
    temperature = models.FloatField(null=True)
    humidity = models.FloatField(null=True)
    elevation = models.FloatField(null=True)
    pressure = models.FloatField(null=True)
    river_discharge = models.FloatField(null=True)

    def __str__(self):
        return f'{self.date} - {self.neighborhood}'