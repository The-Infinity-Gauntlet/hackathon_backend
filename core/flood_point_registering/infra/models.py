from django.db import models
from django.utils import timezone
from core.addressing.infra.models import City, Neighborhood


class FloodPointRegisterQuerySet(models.QuerySet):
    def active(self, now=None):
        if now is None:
            now = timezone.now()
        return self.filter(created_at__lte=now, finished_at__gte=now)


class Flood_Point_Register(models.Model):
    city = models.ForeignKey(City, on_delete=models.PROTECT)
    neighborhood = models.ForeignKey(Neighborhood, on_delete=models.PROTECT)
    possibility = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    finished_at = models.DateTimeField(db_index=True)
    props = models.JSONField()

    objects = FloodPointRegisterQuerySet.as_manager()

    def __str__(self):
        nb = getattr(self, "neighborhood", None)
        ct = getattr(self, "city", None)
        nb_name = getattr(nb, "name", str(nb)) if nb is not None else "?"
        ct_name = getattr(ct, "name", str(ct)) if ct is not None else "?"
        return f"{self.possibility} - {nb_name} ({ct_name})"
