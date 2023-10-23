from django.urls import path
from .views import MyTokenObtainPairView, RegisterView, GetUserView

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view()),
    path("register/", RegisterView.as_view()),
    path("users/", GetUserView.as_view()),
]
