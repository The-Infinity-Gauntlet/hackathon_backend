from rest_framework import serializers


class StreamSnapshotSerializer(serializers.Serializer):
    stream_url = serializers.CharField()
    timeout_seconds = serializers.FloatField(required=False, min_value=0.5, default=5.0)


class StreamBatchSerializer(serializers.Serializer):
    stream_url = serializers.CharField()
    interval_seconds = serializers.FloatField(required=False, min_value=0.1, default=2.0)
    max_iterations = serializers.IntegerField(required=False, min_value=1, max_value=20, default=3)