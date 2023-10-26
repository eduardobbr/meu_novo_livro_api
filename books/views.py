from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from books.models import Book
from .serializers import BookSerializer, GetAllBooksSerializer
from .serializers import GetOneBookSerializer
from .permissions import IsOwner


class BookView(APIView):
    serializer_class = GetAllBooksSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        books = Book.objects.all()
        book_serializer = GetAllBooksSerializer(books, many=True)
        return Response(book_serializer.data, 200)


class CreateBookView(generics.CreateAPIView):
    query_set = Book.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BookSerializer

    def post(self, request):
        data = request.data
        cover = request.POST.get('cover', False)
        data['user'] = request.user.id
        new_book = Book.objects.create(name=data['name'],
                                       content=data['content'],
                                       synopsis=data['synopsis'],
                                       value=data['value'],
                                       production=data['production'],
                                       cover=cover,
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
        serializer_book = BookSerializer(new_book, data)
        if serializer_book.is_valid():
            serializer_book.save()
            return Response(serializer_book.data, 201)
        return Response(serializer_book.errors, 400)


class OneBookAuthView(generics.CreateAPIView):
    queryset = Book.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    serializer_class = GetOneBookSerializer

    def get_object(self, pk, request):
        book = Book.objects.get(pk=pk)
        self.check_object_permissions(request, book)
        return book

    def patch(self, request, *args, **kwargs):
        id = kwargs['id']
        book = self.get_object(id, request)
        book_serializer = GetOneBookSerializer(book, data=request.data,
                                               partial=True)

        if (book_serializer.is_valid()):
            book_serializer.save()
            return Response(book_serializer.data, 200)
        return Response(book_serializer.errors, 400)
