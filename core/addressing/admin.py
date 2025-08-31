from django.contrib import admin
from core.addressing.infra.models import Address, Neighborhood, Region


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "street",
        "number",
        "city",
        "state",
        "country",
        "zipcode",
        "updated_at",
    )
    search_fields = ("street", "city", "zipcode")
    list_filter = ("city", "state", "country")
    list_per_page = 25


@admin.register(Neighborhood)
class NeighborhoodAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "region", "updated_at")
    search_fields = ("name", "city")
    list_filter = ("city", "region")
    autocomplete_fields = ("region",)


@admin.register(Region)
class RegionAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "updated_at")
    search_fields = ("name", "city")
    list_filter = ("city",)
