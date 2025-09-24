from __future__ import annotations
from django.utils.translation import gettext_lazy as _
from rest_framework import exceptions
from rest_framework_simplejwt.authentication import JWTAuthentication as SimpleJWTAuth
from rest_framework_simplejwt.tokens import RefreshToken

from core.users.infra.models import User


class AppJWTAuthentication(SimpleJWTAuth):
	def get_user(self, validated_token):  # type: ignore[override]
		user_id = validated_token.get("user_id")
		if not user_id:
			raise exceptions.AuthenticationFailed(_("Invalid token: no user_id"))
		try:
			return User.objects.get(id=user_id)
		except User.DoesNotExist:
			raise exceptions.AuthenticationFailed(_("User not found"))


def generate_tokens_for_user(user: User) -> dict:
	refresh = RefreshToken.for_user(user)
	return {
		"access": str(refresh.access_token),
		"refresh": str(refresh),
	}
