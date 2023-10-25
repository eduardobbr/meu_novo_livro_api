from django.urls import path
from .views import BookView, CreateBookView, OneBookAuthView

urlpatterns = [
    path('books/', BookView.as_view()),
    path('books/create/', CreateBookView.as_view()),
    path('books/<int:id>/', OneBookAuthView.as_view()),
]
