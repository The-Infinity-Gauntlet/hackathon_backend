from django.db import models
from django.utils import timezone
from core.addressing.infra.models import Region, Neighborhood


class FloodPointRegisterQuerySet(models.QuerySet):
    def active(self, now=None):
        if now is None:
            now = timezone.now()
        return self.filter(created_at__lte=now, finished_at__gte=now)


class Flood_Point_Register(models.Model):
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.PROTECT)
    possibility = models.FloatField()
    created_at = models.DateTimeField(db_index=True)
    finished_at = models.DateTimeField(db_index=True)
    props = models.JSONField()

    objects = FloodPointRegisterQuerySet.as_manager()

    def __str__(self):
        return f"{self.possibility} - {self.neighborhood} ({self.region})"
