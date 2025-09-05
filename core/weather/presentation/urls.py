from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.weather.presentation.views.WeatherSearch import WeatherSearch
from core.weather.presentation.views.WeatherViewSet import WeatherViewSet

router = DefaultRouter()
router.register(r"weather", WeatherViewSet, basename="weather")

urlpatterns = [
    path('', include(router.urls)),
    path("search/", WeatherSearch.as_view(), name="weather-search"),
]