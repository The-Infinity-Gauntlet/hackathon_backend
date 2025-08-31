from django.db import models
import uuid


class Camera(models.Model):
    class CameraStatus(models.IntegerChoices):
        ACTIVE = 1, "ACTIVE"
        INACTIVE = 2, "INACTIVE"
        OFFLINE = 3, "OFFLINE"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    status = models.IntegerField(
        choices=CameraStatus.choices, default=CameraStatus.OFFLINE
    )
    video_url = models.CharField(max_length=512, unique=True)
    description = models.CharField(max_length=255, blank=True)
    address_id = models.CharField(max_length=255, blank=True)
    neighborhood = models.ForeignKey(
        "addressing.Neighborhood",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="cameras",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:  # pragma: no cover
        return f"Camera {self.id} ({self.get_status_display()})"


class FloodDetectionRecord(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    camera = models.ForeignKey(
        Camera, on_delete=models.CASCADE, related_name="detections"
    )
    is_flooded = models.BooleanField()
    confidence = models.FloatField()
    prob_normal = models.FloatField()
    prob_flooded = models.FloatField()
    image = models.ImageField(
        upload_to="flood_detections/%Y/%m/%d/", null=True, blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Flood detection record"
        verbose_name_plural = "Flood detection records"
        indexes = [
            models.Index(fields=["created_at"]),
            models.Index(fields=["confidence"]),
        ]
