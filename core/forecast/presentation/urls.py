from django.urls import path, include
from rest_framework.routers import DefaultRouter
from core.forecast.presentation.views.ForecastApiView import PredictView
from core.forecast.presentation.views.ForecastViewSet import ForecastViewSet

router = DefaultRouter()
router.register(r"foresee", ForecastViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path("forecasts/", PredictView.as_view(), name="forecasts"),
]