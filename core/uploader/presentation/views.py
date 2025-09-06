from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from core.uploader.presentation.serializers import UploadSerializer
from core.uploader.infra.django_storage_uploader import DjangoStorageUploader
from core.uploader.application.services import UploadBinaryService


class GenericUploadView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        f = serializer.validated_data["file"]
        path = serializer.validated_data.get("path") or f"misc/{f.name}"
        content_type = serializer.validated_data.get("content_type") or getattr(f, "content_type", None)

        data = f.read()
        service = UploadBinaryService(DjangoStorageUploader())
        result = service.execute(data=data, path=path, content_type=content_type)
        return Response(
            {
                "url": result.url,
                "path": result.path,
                "size": result.size,
                "content_type": result.content_type,
            },
            status=status.HTTP_201_CREATED,
        )
