from django.db import models
import uuid


class City(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=120, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["name"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return self.name


class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    street = models.CharField(max_length=255)
    number = models.CharField(max_length=50, blank=True)
    city = models.CharField(max_length=120)
    state = models.CharField(max_length=80, blank=True)
    country = models.CharField(max_length=120, default="Brazil")
    zipcode = models.CharField(max_length=32, blank=True)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    neighborhood = models.ForeignKey(
        "Neighborhood",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="addresses",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["zipcode"]),
            models.Index(fields=["neighborhood"]),
            models.Index(fields=["latitude", "longitude"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        base = f"{self.street}"
        if self.number:
            base += f", {self.number}"
        return f"{base} - {self.city}/{self.state or ''}"


class Neighborhood(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    city_ref = models.ForeignKey(
        "addressing.City",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="neighborhoods",
    )
    region = models.ForeignKey(
        "Region",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="neighborhoods",
    )
    props = models.JSONField(default=dict, blank=True)
    # Store area in km^2 as a first-class field; geometry remains inside props
    area_km2 = models.FloatField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["city"]),
            models.Index(fields=["name"]),
            models.Index(fields=["region"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Neighborhood {self.name} - {self.city}"


class Region(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    city = models.CharField(max_length=120)
    city_ref = models.ForeignKey(
        "addressing.City",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="regions",
    )
    props = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["city"]),
        ]

    def __str__(self) -> str:  # pragma: no cover
        return f"Region {self.name} - {self.city}"
