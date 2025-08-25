from rest_framework import serializers
from core.weather.infra.models import Weather

class WeatherModelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Weather
        fields = '__all__'