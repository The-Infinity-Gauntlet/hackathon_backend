from rest_framework import serializers


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField()
    path = serializers.CharField(required=False)
    content_type = serializers.CharField(required=False, allow_blank=True)
