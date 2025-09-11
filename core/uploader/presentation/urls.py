from django.urls import path
from core.uploader.presentation.views import GenericUploadView

urlpatterns = [
    path("", GenericUploadView.as_view(), name="generic-upload"),
]
