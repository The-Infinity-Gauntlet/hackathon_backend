from rest_framework import serializers

class OccurrenceSerializer(serializers.Serializer):
    date = serializers.DateField()
    situation = serializers.CharField(source='get_situation_display')
    type = serializers.CharField()
    neighborhood = serializers.CharField()