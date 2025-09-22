from django.contrib import admin
from core.flood_point_registering.infra.models import Flood_Point_Register


@admin.register(Flood_Point_Register)
class Flood_Points(admin.ModelAdmin):
    list_display = (
        "neighborhood",
        "region",
        "created_at",
        "finished_at",
        "possibility",
    )
    search_fields = ("neighborhood__name", "region__name")
