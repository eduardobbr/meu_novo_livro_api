from .models import User
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer, MyTokenObtainPairSerializer
from .serializers import GetUsersSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = RegisterSerializer


class GetUserView(generics.CreateAPIView):
    serializer_class = GetUsersSerializer

    def get(self, request, *args, **kwargs):
        user = User.objects.all()
        user_serializer = GetUsersSerializer(user, many=True)
        return Response(user_serializer.data, 200)
