from dataclasses import dataclass
from typing import Tuple

from rest_framework_simplejwt.tokens import RefreshToken

from core.users.domain.entities import User
from core.users.domain.repository import UserRepository


@dataclass
class AuthTokens:
    access: str
    refresh: str


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    # Cadastro simples com senha
    def register_user(self, name: str, email: str, password: str | None = None) -> User:
        existing = self.user_repository.get_by_email(email)
        if existing:
            return existing
        user = User(id=None, name=name, email=email)
        user = self.user_repository.save(user)
        if password and user.id:
            self.user_repository.set_password(user.id, password)
        return user

    # Login retorna tokens
    def login(self, email: str, password: str) -> Tuple[User, AuthTokens]:
        user = self.user_repository.verify_password(email, password)
        if not user:
            raise ValueError("Credenciais inválidas")

        # Construct tokens with SimpleJWT minimal payload
        class _Obj:
            id = user.id
            email = user.email

        refresh = RefreshToken.for_user(_Obj)  # type: ignore[arg-type]
        return user, AuthTokens(access=str(refresh.access_token), refresh=str(refresh))
