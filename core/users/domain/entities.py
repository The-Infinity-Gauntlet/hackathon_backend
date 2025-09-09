from datetime import date, datetime, timezone
from enum import Enum
from typing import Optional


class User:

    class UserType(str, Enum):
        ADMIN = "admin"
        STANDARD = "standard"

        @classmethod
        def from_value(cls, value: "User.UserType | str") -> "User.UserType":
            if isinstance(value, User.UserType):
                return value
            v = str(value).strip().lower()
            if v == "standart":
                v = "standard"
            return cls(v)

    def __init__(
        self,
        id: Optional[int],
        name: str,
        email: str,
        date_of_birth: date | datetime | str,
        google_sub: str,
        profile_picture: str,
        create_at: datetime | str | None,
        update_at: datetime | str | None,
        type: "User.UserType | str" = UserType.STANDARD,
    ) -> None:
        self.id: Optional[int] = id
        self.name: str = name
        self.email: str = email
        self.date_of_birth: date = self._to_date(date_of_birth)
        self.google_sub: str = google_sub
        self.profile_picture: str = profile_picture
        now_utc = datetime.now(timezone.utc)
        created = self._to_datetime(create_at) if create_at is not None else now_utc
        updated = self._to_datetime(update_at) if update_at is not None else created
        self.create_at: datetime = created
        self.update_at: datetime = updated

        self.type: User.UserType = self.UserType.from_value(type)

    @staticmethod
    def _to_date(value: date | datetime | str) -> date:
        if isinstance(value, date) and not isinstance(value, datetime):
            return value
        if isinstance(value, datetime):
            return value.date()
        text = str(value).strip()
        if "T" in text:
            text = text.split("T", 1)[0]
        return date.fromisoformat(text)

    @staticmethod
    def _to_datetime(value: datetime | str) -> datetime:
        if isinstance(value, datetime):
            return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
        dt = datetime.fromisoformat(str(value))
        return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)
