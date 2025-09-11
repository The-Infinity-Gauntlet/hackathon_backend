from rest_framework import serializers
from core.users.infra.models import User as DjangoUserModel


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=100)
    email = serializers.EmailField()
