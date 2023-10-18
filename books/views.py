from rest_framework.views import APIView
from rest_framework.response import Response
from books.models import Book
from .serializers import BookSerializer
from rest_framework import generics
from rest_framework.permissions import AllowAny
from users.models import User

class BookView(APIView):
    serializer_class = BookSerializer

    def get(self, request):
        books = Book.objects.all()
        book_serializer = BookSerializer(books, many=True)
        return Response(book_serializer.data, 200)
    
    def post(self, request):
        data = request.data
        new_book = Book.objects.create(name=data['name'], content=data['content'],
                            synopsis=data['synopsis'], value=data['value'],
                            production=data['production'], cover=data['cover'],
                            title=data['title'], subtitle=data['subtitle'],
                            author=data['author'], isbn=data['isbn'],
                            public_target=data['public_target'],
                            keywords=data['keywords'],
                            book_style=data['book_style'], price=data['price'],
                            user=User.objects.get(id=data['user'])
                            )
        new_book.save()
        return Response(data, 201)
        
class CreateBookView(generics.CreateAPIView):
    query_set= Book.objects.all()
    permission_classes=(AllowAny,)
    serializer_class=BookSerializer