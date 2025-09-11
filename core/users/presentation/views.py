from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from core.users.presentation.serializers import UserSerializer
from core.users.infra.models import User
from core.users.app.services import UserService
from core.users.infra.repository import DjangoUserRepository

# Create your views here.


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        repo = DjangoUserRepository()
        service = UserService(repo)
        user = service.register_user(
            name=serializer.validated_data["name"],
            email=serializer.validated_data["email"],
        )
        response_serializer = self.get_serializer(user)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
