from django.urls import path
from .views import MyTokenObtainPairView, RegisterView

urlpatterns = [
    path("login/", MyTokenObtainPairView.as_view()),
    path("register/", RegisterView.as_view()),
]
