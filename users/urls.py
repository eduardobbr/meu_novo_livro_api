from django.urls import path
from rest_framework_simplejwt import views

urlpatterns = [
    path('login/', views.TokenObtainPairView.as_view()),
    path('login/refresh/', views.TokenRefreshView.as_view()),
]