from django.urls import path
from .views import MyTokenObtainPairView, RegisterView, GetUserView
from .views import PatchUserView

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view()),
    path("register/", RegisterView.as_view()),
    path("users/", GetUserView.as_view()),
    path("users/<int:id>/", PatchUserView.as_view()),
]
