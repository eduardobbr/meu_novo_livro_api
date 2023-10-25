from rest_framework.views import APIView
from rest_framework.response import Response
from books.models import Book
from .serializers import BookSerializer, BookSerializerGetAll
from rest_framework import generics, permissions


class BookView(APIView):
    serializer_class = BookSerializerGetAll
    queryset = Book.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        books = Book.objects.all()
        book_serializer = BookSerializerGetAll(books, many=True)
        return Response(book_serializer.data, 200)

    # def patch(self, request, *args, **kwargs):
    #     return Response(request, 200)


class CreateBookView(generics.CreateAPIView):
    query_set = Book.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BookSerializer

    def post(self, request):
        data = request.data
        new_book = Book.objects.create(name=data['name'],
                                       content=data['content'],
                                       synopsis=data['synopsis'],
                                       value=data['value'],
                                       production=data['production'],
                                       cover=data['cover'],
                                       title=data['title'],
                                       subtitle=data['subtitle'],
                                       author=data['author'],
                                       isbn=data['isbn'],
                                       public_target=data['public_target'],
                                       keywords=data['keywords'],
                                       book_style=data['book_style'],
                                       price=data['price'],
                                       user=request.user
                                       )
        new_book.save()
        return Response(data, 201)
