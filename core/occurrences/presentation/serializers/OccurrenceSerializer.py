from rest_framework import serializers
from core.occurrences.infra.models import Occurrence, get_neighborhood


class OccurrenceSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    date = serializers.DateField()
    situation = serializers.ChoiceField(choices=Occurrence.Situation.choices)
    # Expose human-readable label alongside the integer value
    situation_display = serializers.CharField(
        source="get_situation_display", read_only=True
    )
    type = serializers.CharField(max_length=80)
    neighborhood = serializers.ChoiceField(choices=get_neighborhood())

    def create(self, validated_data):
        return Occurrence.objects.create(**validated_data)

    def update(self, instance: Occurrence, validated_data):
        for field in ["date", "situation", "type", "neighborhood"]:
            if field in validated_data:
                setattr(instance, field, validated_data[field])
        instance.save()
        return instance
