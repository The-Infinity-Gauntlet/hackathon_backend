from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.users.presentation.viewsets import UsersViewSet

router = DefaultRouter()
router.register(r"", UsersViewSet, basename="users")

urlpatterns = [
    path("", include(router.urls)),
]
