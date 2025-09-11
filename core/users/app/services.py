from core.users.domain.entities import User
from core.users.domain.repository import UserRepository


class UserService:
    def __init__(self, user_repository: UserRepository) -> None:
        self.user_repository = user_repository

    def register_user(self, name: str, email: str) -> User:
        user = User(id=None, name=name, email=email)
        return self.user_repository.save(user)
