from __future__ import annotations
from typing import Optional, Tuple

from rest_framework.authentication import BaseAuthentication
from rest_framework.request import Request
from rest_framework.exceptions import AuthenticationFailed
from django.utils.translation import gettext_lazy as _


class AppJWTAuthentication(BaseAuthentication):
    """Thin wrapper around SimpleJWT's JWTAuthentication with lazy import.

    Defers importing rest_framework_simplejwt until authenticate() is called to
    avoid AppRegistryNotReady during DRF settings initialization.
    """

    def authenticate(self, request: Request) -> Optional[Tuple[object, object]]:  # type: ignore[override]
        # Lazy import to avoid early Django app loading
        from rest_framework_simplejwt.authentication import (
            JWTAuthentication as SimpleJWTAuth,
        )

        inner = SimpleJWTAuth()
        # Manually drive the token flow to avoid SimpleJWT's get_user()
        header = inner.get_header(request)
        if header is None:
            return None
        raw_token = inner.get_raw_token(header)
        if raw_token is None:
            return None
        validated_token = inner.get_validated_token(raw_token)
        # Replace user with our domain User fetched by id claim
        user_id = validated_token.get("user_id")
        if not user_id:
            raise AuthenticationFailed(_("Invalid token: no user_id"))
        from core.users.infra.models import User

        try:
            user = User.objects.get(id=user_id)
        except User.DoesNotExist:
            raise AuthenticationFailed(_("User not found"))
        return user, validated_token
