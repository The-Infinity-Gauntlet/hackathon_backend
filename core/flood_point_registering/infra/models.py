from django.db import models
from django.utils import timezone
from core.addressing.infra.models import Region, Neighborhood


class FloodPointRegisterQuerySet(models.QuerySet):
    def active(self, now=None):
        if now is None:
            now = timezone.now()
        return self.filter(created_at__lte=now, finished_at__gte=now)


class Flood_Point_Register(models.Model):
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.PROTECT)
    region = models.ForeignKey(Region, on_delete=models.PROTECT)
    possibility = models.FloatField()
    # Match migrations: indexed DateTimeFields (no auto_now*)
    created_at = models.DateTimeField(db_index=True)
    finished_at = models.DateTimeField(db_index=True)
    props = models.JSONField()

    objects = FloodPointRegisterQuerySet.as_manager()

    def __str__(self):
        nb = getattr(self, "neighborhood", None)
        rg = getattr(self, "region", None)
        nb_name = getattr(nb, "name", str(nb)) if nb is not None else "?"
        rg_name = getattr(rg, "name", str(rg)) if rg is not None else "?"
        return f"{self.possibility} - {nb_name} ({rg_name})"
