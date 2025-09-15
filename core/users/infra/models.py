from django.db import models
import uuid


class User(models.Model):
    class UserType(models.TextChoices):
        ADMIN = "admin", "ADMIN"
        STANDARD = "standard", "STANDARD"

    id: uuid.UUID = models.UUIDField(
        primary_key=True, default=uuid.uuid4, editable=False
    )
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True, max_length=300, db_index=True)
    date_of_birth = models.DateField()
    google_sub = models.CharField(max_length=255, unique=True, db_index=True)
    profile_picture = models.URLField(max_length=512, blank=True)
    type = models.CharField(
        max_length=20, choices=UserType.choices, default=UserType.STANDARD
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.name} <{self.email}> ({self.get_type_display()})"

    class Meta:
        ordering = ["name"]
        indexes = [
            models.Index(fields=["email"]),
            models.Index(fields=["google_sub"]),
        ]
