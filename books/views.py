from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from books.models import Book
from .serializers import BookSerializer, GetAllBooksSerializer
from .serializers import GetOneBookSerializer
from .permissions import IsOwner
from weasyprint import HTML, CSS
from django.http import HttpResponse
from .style import css_style, stylesheet, page_style
import os
from pathlib import Path


class BookView(APIView):
    serializer_class = GetAllBooksSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        user = request.query_params.get('user')

        if (user):
            books = Book.objects.filter(user=user)
            book_serializer = GetAllBooksSerializer(books, many=True)
            return Response(book_serializer.data, 200)

        books = Book.objects.all()
        book_serializer = GetAllBooksSerializer(books, many=True)
        return Response(book_serializer.data, 200)


class CreateBookView(generics.CreateAPIView):
    query_set = Book.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = BookSerializer

    def post(self, request):
        data = request.data
        cover = request.POST.get('cover', None)
        _mutable = data._mutable
        data._mutable = True
        data['user'] = request.user.id
        data['value'] = 0
        data['price'] = 0
        data._mutable = _mutable
        new_book = Book.objects.create(name=data['name'],
                                       content=data['content'],
                                       synopsis=data['synopsis'],
                                       value=data['value'],
                                       production=True,
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
        data = request.data
        cover = 'cover' in data and data['cover']

        if not cover:
            cover = None

        data_set = {
            'content': data['content'],
            'synopsis': data['synopsis'],
            'production': data['production'],
            'title': data['title'],
            'subtitle': data['subtitle'],
            'author': data['author'],
            'isbn': data['isbn'],
            'public_target': data['public_target'],
            'keywords': data['keywords'],
            'book_style': data['book_style'],
            'cover': cover,
            'user': request.user.id
        }

        book_serializer = GetOneBookSerializer(book, data=data_set,
                                               partial=True)

        if (book_serializer.is_valid()):
            book_serializer.save()
            return Response(book_serializer.data, 200)
        return Response(book_serializer.errors, 400)

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        book = self.get_object(id, request)
        book_serializer = GetOneBookSerializer(book, data=request.data,
                                               partial=True)

        if (book_serializer.is_valid()):
            return Response(book_serializer.data, 200)
        return Response(book_serializer.errors, 400)


class ConvertDownloadBookView(generics.CreateAPIView):
    queryset = Book.objects.all()
    permission_classes = (permissions.IsAuthenticated, IsOwner,)
    serializer_class = GetOneBookSerializer

    def get_object(self, pk, request):
        book = Book.objects.get(pk=pk)
        self.check_object_permissions(request, book)
        return book

    def generate_epub(self, book):
        content = book['content']
        content_filtered = content.split('<h1')
        path = 'bookGen'
        if not os.path.exists(path):
            os.mkdir(path)

        book_path = f'{path}/{book['name']}'
        if not os.path.exists(book_path):
            os.mkdir(book_path)

        caps = []
        content_filtered.pop(0)

        for cap in content_filtered:
            cap_title = ''
            cap_filter = cap.split('</h1>')
            if ('<em>' in cap_filter[0]):
                cap_filter = cap_filter[0].split('<em>')
                cap_filter = cap_filter[1].split('</em>')
                cap_title = cap_filter[0]
            elif ('<strong>' in cap_filter[0]):
                cap_filter = cap_filter[0].split('<strong>')
                cap_filter = cap_filter[1].split('</strong>')
                cap_title = cap_filter[0]

            cap_text = f'<h1{cap}'
            cap_xml = f'''<?xml version="1.0" encoding="utf-8"?>
                    <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN"
                    "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">

                    <html xmlns="http://www.w3.org/1999/xhtml">
                    <head>
                        <title>{cap_title}</title>
                    </head>

                    <body>
                        <div class="editor ql-editor">
                            {cap_text}
                        </div>
                    </body>
                    </html>'''

            Path(f'{book_path}/{cap_title}.xhtml').touch()
            with open(f'{book_path}/{cap_title}.xhtml', 'w') as f:
                f.write(cap_xml)

            caps.append({cap_title, cap_xml})

        Path(f'{book_path}/mimetype').touch()
        with open(f'{book_path}/mimetype', 'w') as f:
            f.write('application/epub+zip ')

        Path(f'{book_path}/stylesheet.css').touch()
        with open(f'{book_path}/stylesheet.css', 'w') as f:
            f.write(stylesheet)

        Path(f'{book_path}/page_styles.css').touch()
        with open(f'{book_path}/page_styles.css', 'w') as f:
            f.write(page_style)

        return caps

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        book = self.get_object(id, request)
        book_serializer = GetOneBookSerializer(book)
        book_data = book_serializer.data
        teste = self.generate_epub(book_data)

        render_str = f'<div><img src="http://127.0.0.1:8000/{
            book_data["cover"]}" class="cover"/> </div>{
            book_data['content']}'
        html_pdf = HTML(string=render_str)
        css_pdf = CSS(string=css_style)
        pdf = html_pdf.write_pdf(stylesheets=[css_pdf])

        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename=book.pdf'

        return response
