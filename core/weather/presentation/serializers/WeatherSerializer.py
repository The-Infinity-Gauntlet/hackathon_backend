from rest_framework import serializers

class WeatherSerializer(serializers.Serializer):
    start = serializers.DateField(required=True)
    end = serializers.DateField(required=True)
    # Somente start e end serializados porque os demais virão diretamente de fontes externas