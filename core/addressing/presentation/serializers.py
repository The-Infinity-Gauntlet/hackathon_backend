from rest_framework import serializers
from core.addressing.infra.models import Neighborhood, Region

class NeighborhoodSerializer(serializers.Serializer):
    class Meta:
        model = Neighborhood
        fields = ['id', 'name']

class RegionSerializer(serializers.Serializer):
    class Meta:
        model = Region
        fields = ['id', 'name', 'region']