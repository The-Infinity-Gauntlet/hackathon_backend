from core.users.domain.repository import UserRepository
from core.users.domain.entities import User as DomainUser
from core.users.infra.models import User as DjangoUser
from typing import Optional, List


class DjangoUserRepository(UserRepository):
    def save(self, user: DomainUser) -> Optional[DomainUser]:
        if not user:
            return None
        try:
            if user.id:
                user_obj = DjangoUser.objects.get(id=user.id)
                user_obj.name = user.name
                user_obj.email = user.email
                user_obj.save()
            else:
                user_obj = DjangoUser.objects.create(name=user.name, email=user.email)
            return DomainUser(id=user_obj.id, name=user_obj.name, email=user_obj.email)
        except Exception as e:
            # Log exception if needed
            return None
