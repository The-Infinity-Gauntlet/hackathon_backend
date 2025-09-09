from abc import ABC, abstractmethod
from typing import Optional, Iterable

from core.users.domain.entities import User


class UserRepository(ABC):
    """Porta de repositório para entidade de usuário no domínio."""

    @abstractmethod
    def save(self, user: User) -> User:
        """Cria um novo usuário e retorna a entidade persistida."""
        raise NotImplementedError

    @abstractmethod
    def update(self, user: User) -> User:
        """Atualiza um usuário existente e retorna a entidade atualizada."""
        raise NotImplementedError

    @abstractmethod
    def delete(self, user_id: int) -> None:
        """Remove um usuário pelo id."""
        raise NotImplementedError

    @abstractmethod
    def get_by_id(self, user_id: int) -> Optional[User]:
        """Obtém um usuário pelo id (ou None se não encontrado)."""
        raise NotImplementedError

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Obtém um usuário pelo e-mail (ou None)."""
        raise NotImplementedError

    @abstractmethod
    def list(self, *, page: int = 1, page_size: int = 50) -> Iterable[User]:
        """Lista usuários, com paginação simples."""
        raise NotImplementedError
