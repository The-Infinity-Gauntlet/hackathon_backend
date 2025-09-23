from __future__ import annotations
from typing import Any

from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdmin(BasePermission):
    """Permite acesso apenas para usuários com type == 'admin'."""

    message = "Apenas administradores podem acessar."

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        user: Any = getattr(request, "user", None)
        return bool(
            user
            and getattr(user, "is_authenticated", False)
            and getattr(user, "type", None) == "admin"
        )


class IsAdminOrReadOnly(BasePermission):
    """Permite leitura para todos; escrita apenas para administradores."""

    message = "Apenas administradores podem alterar recursos."

    def has_permission(self, request, view) -> bool:  # type: ignore[override]
        if request.method in SAFE_METHODS:
            return True
        return IsAdmin().has_permission(request, view)
