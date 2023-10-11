from rest_framework.views import APIView
from rest_framework.response import Response
from books.models import Book
from django.forms.models import model_to_dict

class BookView(APIView):
    def get(self, request, *args, **kwargs):
        return Response({'book': Book.objects.all()})

    def post(self, request, *args, **kwargs):
        return Response({'book': 'post'})
    
    
class OneBookView(APIView):
    def get(self, request, book_id, *args, **kwargs):
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Livro não encontrado'}, status=404)
        
        book_dict = model_to_dict(book)

        return Response(book_dict)
    
    def patch(self, request, book_id, *args, **kwargs):
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Livro não encontrado'}, status=404)
        
        book_dict = model_to_dict(book)

        return Response(book_dict)
    
    def delete(self, request, book_id, *args, **kwargs):
        try:
            book = Book.objects.get(pk=book_id)
        except Book.DoesNotExist:
            return Response({'error': 'Livro não encontrado'}, status=404)
        
        book.delete()
        return Response({'success': True}, status=204)
