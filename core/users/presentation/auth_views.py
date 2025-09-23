from __future__ import annotations
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions, serializers
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView

from core.users.infra.models import User


def generate_tokens_for_user(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh),
    }


class EmailTokenObtainPairSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, min_length=6)

    def validate(self, attrs):
        email = attrs.get("email", "").lower().strip()
        password = attrs.get("password", "")
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed(_("Credenciais inválidas"))
        if not user.check_password(password):
            raise exceptions.AuthenticationFailed(_("Credenciais inválidas"))

        tokens = generate_tokens_for_user(user)
        return {"access": tokens["access"], "refresh": tokens["refresh"]}


class EmailTokenObtainPairView(TokenObtainPairView):
    serializer_class = EmailTokenObtainPairSerializer
