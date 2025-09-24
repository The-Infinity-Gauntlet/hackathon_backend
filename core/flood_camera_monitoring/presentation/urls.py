from django.urls import path
from core.flood_camera_monitoring.presentation.viewsets import (
    FloodMonitoringViewSet,
    HealthcheckView,
    HlsLoopInfoView,
    HlsPredictView,
)

urlpatterns = [
    path(
        "stream/snapshot",
        FloodMonitoringViewSet.as_view({"post": "predict_snapshot"}),
        name="stream-snapshot-detect",
    ),
    path(
        "predict/all/",
        FloodMonitoringViewSet.as_view({"get": "predict_all"}),
        name="predict-all-cameras",
    ),
    path(
        "cameras/",
        FloodMonitoringViewSet.as_view({"get": "cameras"}),
        name="cameras-list",
    ),
    path("health/", HealthcheckView.as_view(), name="health"),
    # Simplified HLS live loop endpoints
    path("demo", HlsLoopInfoView.as_view(), name="hls-demo-info"),
    path("demo/predict", HlsPredictView.as_view(), name="hls-demo-predict"),
]
