from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.addressing.presentation.viewsets import AddressingViewSet

router = DefaultRouter()
router.register(r"", AddressingViewSet, basename="addressing")

urlpatterns = [
    path("", include(router.urls)),
]
