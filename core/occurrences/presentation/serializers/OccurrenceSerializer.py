from rest_framework import serializers

class OccurrenceSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    situation = serializers.CharField(source='get_situation_display')
    type = serializers.CharField()
    neighborhood = serializers.CharField()