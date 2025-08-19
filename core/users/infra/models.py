from django.db import models
import uuid


class User(models.Model):
    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)

    def __str__(self) -> str:
        return f"{self.name} <{self.email}>"
