from django.contrib import admin
from core.flood_camera_monitoring.infra.models import Camera, FloodDetectionRecord


@admin.register(Camera)
class CameraAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "status",
        "description",
        "video_hls",
        "video_embed",
        "neighborhood",
        "latitude",
        "longitude",
        "updated_at",
    )
    list_filter = ("status",)
    search_fields = (
        "id",
        "video_hls",
        "video_embed",
        "description",
        "neighborhood__name",
    )
    autocomplete_fields = ("neighborhood",)
    list_select_related = ("neighborhood",)
    list_per_page = 25


@admin.register(FloodDetectionRecord)
class FloodDetectionRecordAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "camera_description",
        "is_flooded",
        "medium",
        "confidence",
        "prob_normal",
        "prob_flooded",
        "prob_medium",
        "created_at",
    )
    list_filter = ("is_flooded", "medium")
    search_fields = ("camera__id", "camera__description")
    list_select_related = ("camera",)
    list_per_page = 25

    @admin.display(ordering="camera__description", description="Câmera")
    def camera_description(self, obj):
        return getattr(obj.camera, "description", "")
