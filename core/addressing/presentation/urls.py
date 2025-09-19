from django.urls import path, include
from core.addressing.presentation.views import NeighborhoodGeoJSONView, NeighborhoodViewSet, RegionViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r"neighborhood", NeighborhoodViewSet)
router.register(r"region", RegionViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("dados_geograficos", NeighborhoodGeoJSONView.as_view()),
]
