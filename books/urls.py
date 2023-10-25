from django.urls import path
from .views import BookView, CreateBookView

urlpatterns = [
    path('books/', BookView.as_view()),
    path('books/create/', CreateBookView.as_view()),
]
