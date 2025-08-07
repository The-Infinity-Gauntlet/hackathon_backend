from abc import ABC, abstractmethod
from core.users.domain.entities import User


class UserRepository(ABC):
    @abstractmethod
    def save(self, user: User) -> User:
        pass
