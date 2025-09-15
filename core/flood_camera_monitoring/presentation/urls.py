from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.flood_camera_monitoring.presentation.viewsets import FloodMonitoringViewSet

router = DefaultRouter()
router.register(r"", FloodMonitoringViewSet, basename="flood-monitoring")

urlpatterns = [
    path("", include(router.urls)),
]
