from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer
from .serializers import GetUsersSerializer, PatchUsersSerializer
from rest_framework import generics, permissions
from rest_framework.response import Response
from .permissions import IsOwner


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegisterSerializer


class GetUserView(generics.CreateAPIView):
    serializer_class = GetUsersSerializer
    queryset = User.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        user_serializer = GetUsersSerializer(user, many=True)
        return Response(user_serializer.data, 200)


class PatchUserView(generics.CreateAPIView):
    serializer_class = GetUsersSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]
    queryset = User.objects.all()

    def get_object(self, pk):
        return User.objects.get(pk=pk)

    def patch(self, request, *args, **kwargs):
        id = kwargs['id']
        user = self.get_object(id)
        user_serializer = PatchUsersSerializer(user, data=request.data,
                                               partial=True)

        if (user_serializer.is_valid()):
            user_serializer.save()
            return Response(user_serializer.data, 200)
        return Response({'detail': 'Algo deu errado!'}, 400)
