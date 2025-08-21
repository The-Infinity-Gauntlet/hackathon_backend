from django.urls import path
from .views import WeatherSearch

urlpatterns = [
    path("weather/search/", WeatherSearch.as_view(), name="weather-search"),
]