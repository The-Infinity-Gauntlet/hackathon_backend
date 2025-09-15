from typing import Optional, Iterable

from django.contrib.auth.hashers import make_password, check_password

from core.users.domain.entities import User as DomainUser
from core.users.domain.repository import UserRepository
from core.users.infra.models import User as DjangoUser


def _map_django_to_domain(u: DjangoUser) -> DomainUser:
    return DomainUser(
        id=str(u.id),
        name=u.name,
        email=u.email,
        date_of_birth=u.date_of_birth if u.date_of_birth else None,
        google_sub=u.google_sub,
        profile_picture=u.profile_picture or "",
        create_at=u.created_at,
        update_at=u.updated_at,
        type=u.type,
    )


class DjangoUserRepository(UserRepository):
    def save(self, user: DomainUser) -> DomainUser:
        if user.id:
            obj = DjangoUser.objects.get(id=user.id)
            obj.name = user.name
            obj.email = user.email
            obj.profile_picture = user.profile_picture
            obj.type = user.type.value if hasattr(user.type, "value") else str(user.type)
            obj.save()
        else:
            obj = DjangoUser.objects.create(
                name=user.name,
                email=user.email,
                profile_picture=user.profile_picture,
                type=user.type.value if hasattr(user.type, "value") else str(user.type),
            )
        return _map_django_to_domain(obj)

    def update(self, user: DomainUser) -> DomainUser:
        return self.save(user)

    def delete(self, user_id: str) -> None:
        DjangoUser.objects.filter(id=user_id).delete()

    def get_by_id(self, user_id: str) -> Optional[DomainUser]:
        try:
            obj = DjangoUser.objects.get(id=user_id)
            return _map_django_to_domain(obj)
        except DjangoUser.DoesNotExist:
            return None

    def get_by_email(self, email: str) -> Optional[DomainUser]:
        try:
            obj = DjangoUser.objects.get(email=email)
            return _map_django_to_domain(obj)
        except DjangoUser.DoesNotExist:
            return None

    def list(self, *, page: int = 1, page_size: int = 50) -> Iterable[DomainUser]:
        qs = DjangoUser.objects.all().order_by("name")
        start = (page - 1) * page_size
        end = start + page_size
        for u in qs[start:end]:
            yield _map_django_to_domain(u)

    def set_password(self, user_id: str, raw_password: str) -> None:
        try:
            obj = DjangoUser.objects.get(id=user_id)
        except DjangoUser.DoesNotExist:
            return
        obj.set_password(raw_password)
        obj.save(update_fields=["password"])

    def verify_password(self, email: str, raw_password: str) -> Optional[DomainUser]:
        try:
            obj = DjangoUser.objects.get(email=email)
        except DjangoUser.DoesNotExist:
            return None
        if not obj.password:
            return None
        if check_password(raw_password, obj.password):
            return _map_django_to_domain(obj)
        return None
