from django.db import models

class Occurrence(models.Model):
    date = models.DateField()
    class Situation(models.IntegerChoices):
        ALERTA = 1, "alerta"
        ATENCAO = 2, "atencao"
        MOBILIZACAO = 3, "mobilizacao"
        NORMALIDADE = 4, "normalidade"
    situation = models.IntegerField(choices=Situation.choices, default=Situation.NORMALIDADE)
    type = models.CharField(max_length=80)
    neighborhood = models.CharField(max_length=22)

    def __str__(self):
        return f'{self.situation} - {self.date} - {self.neighborhood}'