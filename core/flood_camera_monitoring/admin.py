from django.contrib import admin
from core.flood_camera_monitoring.infra.models import Camera, FloodDetectionRecord


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "video_url",
        "description",
        "address_id",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = ("id", "video_url", "description", "address_id")
    list_per_page = 25


@admin.register(FloodDetectionRecord)
class FloodDetectionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "camera_description",
        "is_flooded",
        "confidence",
        "prob_normal",
        "prob_flooded",
        "created_at",
    )
    list_filter = ("is_flooded",)
    search_fields = ("camera__id", "camera__description")
    list_select_related = ("camera",)
    list_per_page = 25

    @admin.display(ordering="camera__description", description="Câmera")
    def camera_description(self, obj):
        return getattr(obj.camera, "description", "")
