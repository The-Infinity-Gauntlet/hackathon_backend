from django.db import models

class Occurrence(models.Model):
    datetime = models.DateTimeField()
    situation = models.CharField()
    type = models.CharField()
    neighborhood = models.CharField()

    def __str__(self):
        return f'{self.situation} - {self.datetime} - {self.neighborhood}'