from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.uploader.presentation.viewsets import UploadViewSet

router = DefaultRouter(trailing_slash=False)
router.register(r"", UploadViewSet, basename="upload")

urlpatterns = [
    path("", include(router.urls)),
]
