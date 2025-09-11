from django.urls import path
from core.flood_camera_monitoring.presentation.views import (
    StreamSnapshotDetectView,
    StreamBatchDetectView,
    AnalyzeAllCamerasView,
    PredictAllCamerasView,
    CamerasListView,
)

urlpatterns = [
    path(
        "stream/snapshot",
        StreamSnapshotDetectView.as_view(),
        name="stream-snapshot-detect",
    ),
    path("stream/batch", StreamBatchDetectView.as_view(), name="stream-batch-detect"),
    path("analyze/run", AnalyzeAllCamerasView.as_view(), name="analyze-all-cameras"),
    path(
        "predict/all",
        PredictAllCamerasView.as_view(),
        name="predict-all-cameras",
    ),
    path("cameras", CamerasListView.as_view(), name="cameras-list"),
]
