from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.flood_point_registering.presentation.views.RegisterViewSet import FloodPointRegister

router = DefaultRouter()
router.register(r"registering", FloodPointRegister)

urlpatterns = [
    path('', include(router.urls))
]