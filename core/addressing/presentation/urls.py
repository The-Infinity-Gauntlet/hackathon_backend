from django.urls import path
from core.addressing.presentation.views import NeighborhoodGeoJSONView

urlpatterns = [
    path("dados_geograficos", NeighborhoodGeoJSONView.as_view()),
]
