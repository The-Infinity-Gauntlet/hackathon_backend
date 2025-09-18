from django.urls import path
from core.flood_camera_monitoring.presentation.views import (
    StreamSnapshotDetectView,
    StreamBatchDetectView,
    AnalyzeAllCamerasView,
    PredictAllCamerasView,
    CamerasListView,
    HealthcheckView,
    HlsLoopInfoView,
    HlsPredictView,
)

urlpatterns = [
    path(
        "stream/snapshot",
        StreamSnapshotDetectView.as_view(),
        name="stream-snapshot-detect",
    ),
    path(
        "predict/all",
        PredictAllCamerasView.as_view(),
        name="predict-all-cameras",
    ),
    path("cameras", CamerasListView.as_view(), name="cameras-list"),
    path("health", HealthcheckView.as_view(), name="health"),
    # Simplified HLS live loop endpoints
    path("demo", HlsLoopInfoView.as_view(), name="hls-demo-info"),
    path("demo/predict", HlsPredictView.as_view(), name="hls-demo-predict"),
]
