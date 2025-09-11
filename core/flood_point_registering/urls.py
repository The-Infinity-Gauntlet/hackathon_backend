from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.flood_point_registering.presentation.views import RegisterViewSet

router = DefaultRouter()
router.register(r"add_flood_point", RegisterViewSet)

urlpatterns = [
    path('', include(router.urls))
]