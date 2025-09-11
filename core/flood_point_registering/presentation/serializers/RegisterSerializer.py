from rest_framework import serializers

class FloodPointRegisterSerializer(serializers.Serializer):
    city = serializers.CharField(source='get_city_display')
    region = serializers.CharField()
    neighborhood = serializers.CharField()
    possibility = serializers.FloatField()
    created_at = serializers.DateTimeField()
    updated_at = serializers.DateTimeField()
    props = serializers.JSONField()