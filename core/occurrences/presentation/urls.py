from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.occurrences.presentation.views.OccurrenceViewSet import OccurrenceViewSet

router = DefaultRouter()
router.register(r"occurrences", OccurrenceViewSet)

urlpatterns = [
    path('', include(router.urls))
]