from rest_framework import serializers

class OccurrenceSerializer(serializers.Serializer):
    datetime = serializers.DateTimeField()
    situation = serializers.CharField()
    type = serializers.CharField()
    neighborhood = serializers.CharField()
    