from django.contrib import admin
from core.users.infra.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
	list_display = ("id", "name", "email", "type", "created_at")
	search_fields = ("name", "email")
	list_filter = ("type",)
