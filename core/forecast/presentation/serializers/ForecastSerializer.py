from rest_framework import serializers
from core.forecast.infra.models import Forecast

class ForecastSerializer(serializers.ModelSerializer):
    class Meta:
        model = Forecast
        fields = ['latitude', 'longitude', 'date', 'flood', 'probability']