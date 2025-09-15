from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.weather.presentation.views.WeatherViewSet import WeatherViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"weather", WeatherViewSet, basename="weather")

urlpatterns = [
    path("", include(router.urls)),
    # Legacy explicit route preserved for backward compatibility
    path("search/", WeatherViewSet.as_view({"post": "search"}), name="weather-search"),
]
