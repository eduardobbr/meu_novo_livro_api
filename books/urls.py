from django.urls import path
from .views import BookView, OneBookView

urlpatterns = [
    path('books', BookView.as_view()),
    path('books/<int:book_id>', OneBookView.as_view())
]