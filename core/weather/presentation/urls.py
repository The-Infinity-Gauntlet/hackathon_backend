from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.weather.presentation.views import WeatherSearch, WeatherViewSet

router = DefaultRouter()
router.register(r"weahter", WeatherViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("weather/search/", WeatherSearch.as_view(), name="weather-search"),
]