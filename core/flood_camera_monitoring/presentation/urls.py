from django.urls import path
from core.flood_camera_monitoring.presentation.views import (
    StreamSnapshotDetectView,
    StreamBatchDetectView,
    AnalyzeAllCamerasView,
)

urlpatterns = [
    path(
        "stream/snapshot",
        StreamSnapshotDetectView.as_view(),
        name="stream-snapshot-detect",
    ),
    path("stream/batch", StreamBatchDetectView.as_view(), name="stream-batch-detect"),
    path("analyze/run", AnalyzeAllCamerasView.as_view(), name="analyze-all-cameras"),
]
