from django.contrib import admin
from core.weather.infra.models import Weather

@admin.register(Weather)
class WeatherAdmin(admin.ModelAdmin):
    list_display = ("date", "latitude", "longitude", "neighborhood", "rain", "temperature", "umidity", "elevation")
    list_filter = ("date",)
    search_fields = ("latitude", "longitude")