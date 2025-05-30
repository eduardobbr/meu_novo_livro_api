from rest_framework import generics, permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from books.models import Book
from .serializers import BookSerializer, GetAllBooksSerializer
from .serializers import GetOneBookSerializer
from .permissions import IsOwner
import pdfkit
from django.http import HttpResponse
from .style import stylesheet, page_style, nav_style
from .style import title_page_style
import os
from pathlib import Path
from datetime import datetime
import uuid
import shutil


class BookView(APIView):
    serializer_class = GetAllBooksSerializer
    queryset = Book.objects.all()
    permission_classes = [permissions.AllowAny]

    def get(self, request):

        try:
            user = request.query_params.get('user')

            if (user):
                books = Book.objects.filter(user=user)
                book_serializer = GetAllBooksSerializer(books, many=True)
                return Response(book_serializer.data, 200)

            books = Book.objects.all()
            book_serializer = GetAllBooksSerializer(books, many=True)
            return Response(book_serializer.data, 200)
        except Exception as e:
            return Response(e, 400)


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
        cover_path = f'media/books/{book.name}/cover.jpeg'
        if cover and os.path.exists(cover_path):
            os.remove(cover_path)

        if not cover:
            cover = book.cover

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

    def delete(self, request, *args, **kwargs):
        try:
            id = kwargs['id']
            book = self.get_object(id, request)
            book.delete()

            return Response(status=204)

        except Exception as e:
            return Response(e, 400)


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
        book_uuid = uuid.uuid4()
        path = 'bookGen'
        if not os.path.exists(path):
            os.mkdir(path)

        book_path = f'{path}/{book['name']}'
        if not os.path.exists(book_path):
            os.mkdir(book_path)

        caps = []

        class Cap:
            def __init__(self, title, xml, name, cap_number):
                self.title = title
                self.xml = xml
                self.name = name
                self.cap_number = cap_number

        content_filtered.pop(0)

        cap_counter = 1

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
            cap_text = cap_text.replace('<br>', '<br />')
            cap_xml = f'''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{cap_title}</title>
    <link rel="stylesheet" href="stylesheet.css" />
    <link rel="stylesheet" href="page_styles.css" />
</head>

<body>
    <div class="editor ql-editor">
        {cap_text}
    </div>
</body>
</html>'''

            cap_name = f'{book['author']}-{cap_counter}'

            Path(f'{book_path}/{cap_name}.xhtml').touch()
            with open(f'{book_path}/{cap_name}.xhtml', 'w') as f:
                f.write(cap_xml)

            caps.append(Cap(cap_title, cap_xml, cap_name, cap_counter))
            cap_counter += 1

        Path(f'{book_path}/mimetype').touch()
        with open(f'{book_path}/mimetype', 'w') as f:
            f.write('application/epub+zip')

        Path(f'{book_path}/stylesheet.css').touch()
        with open(f'{book_path}/stylesheet.css', 'w') as f:
            f.write(stylesheet)

        Path(f'{book_path}/page_styles.css').touch()
        with open(f'{book_path}/page_styles.css', 'w') as f:
            f.write(page_style)

        Path(f'{book_path}/nav_styles.css').touch()
        with open(f'{book_path}/nav_styles.css', 'w') as f:
            f.write(nav_style)

        Path(f'{book_path}/title_page_style.css').touch()
        with open(f'{book_path}/title_page_style.css', 'w') as f:
            f.write(title_page_style)

        title_page = f"""<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
<!DOCTYPE html>

<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops">
<head>
  <title>{book['title']}</title>
  <link rel="stylesheet" href="stylesheet.css" />
  <link rel="stylesheet" href="title_page_style.css" />
  <link rel="stylesheet" href="page_styles.css" />
</head>
<body>
  <div class="title_div">
    <div>
    <h1>{book['title']}</h1>
    <h2>{book['subtitle']}</h2>
    </div>
    <h2>{book['author']}</h2>
  </div>
</body>
</html>"""

        Path(f'{book_path}/titlepage.xhtml').touch()
        with open(f'{book_path}/titlepage.xhtml', 'w') as f:
            f.write(title_page)

        toc_list = []

        for cap in caps:
            toc_list.append(f"""<navPoint class="chapter" id="{cap.name}" playOrder="{cap.cap_number}">
    <navLabel><text>{cap.title}</text></navLabel>
    <content src="{cap.name}.xhtml"/>
</navPoint>""")

        toc_text = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE ncx PUBLIC "-//NISO//DTD ncx 2005-1//EN" "http://www.daisy.org/z3986/2005/ncx-2005-1.dtd">

<ncx version="2005-1" xml:lang="en" xmlns="http://www.daisy.org/z3986/2005/ncx/">

<head>
    <meta name="dtb:uid" content="{book_uuid}"/>
    <meta name="dtb:depth" content="1"/>
    <meta name="dtb:totalPageCount" content="0"/>
    <meta name="dtb:maxPageNumber" content="0"/>
</head>

<docTitle>
    <text>Sumário</text>
</docTitle>

<docAuthor>
    <text>{book['author']}</text>
</docAuthor>

<navMap>
{''.join(str(cap) for cap in toc_list)}
</navMap>

</ncx>"""

        Path(f'{book_path}/toc.ncx').touch()
        with open(f'{book_path}/toc.ncx', 'w') as f:
            f.write(toc_text)

        nav_list = []

        for cap in caps:
            nav_list.append(f"""<li>
        <a href="{cap.name}.xhtml">{cap.title}</a>
      </li>""")

        nav_text = f"""<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE html>
<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en" xml:lang="en">
<head>
  <title>{book['title']}</title>
  <link rel="stylesheet" href="stylesheet.css" />
  <link rel="stylesheet" href="nav_styles.css" />
  <link rel="stylesheet" href="page_styles.css" />
  <meta charset="utf-8" /></head>
<body epub:type="frontmatter">
  <nav epub:type="toc" id="toc" role="doc-toc">
    <h1>Sumário</h1>
    <ol>
      {''.join(str(cap) for cap in nav_list)}
    </ol>
  </nav>
</body>
</html>"""

        Path(f'{book_path}/nav.xhtml').touch()
        with open(f'{book_path}/nav.xhtml', 'w') as f:
            f.write(nav_text)

        shutil.copytree('bookGen/Fonts', f'{book_path}/Fonts')

        if not os.path.exists(f'{book_path}/META-INF'):
            os.mkdir(f'{book_path}/META-INF')

        Path(f'{book_path}/META-INF/container.xml').touch()
        with open(f'{book_path}/META-INF/container.xml', 'w') as f:
            f.write("""<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
  <rootfiles>
    <rootfile full-path="content.opf" media-type="application/oebps-package+xml" />
  </rootfiles>
</container>""")

        item_list = []

        for cap in caps:
            item_list.append(f"""<item id='{cap.name}' href='{
                             cap.name}.xhtml' media-type="application/xhtml+xml"/>""")

        item_ref_list = []

        for cap in caps:
            item_ref_list.append(f"""<itemref idref='{cap.name}'/>""")
        meta = f"""<?xml version="1.0" encoding="utf-8"?>
<package version="3.0" unique-identifier="{book_uuid}" prefix="rendition: http://www.idpf.org/vocab/rendition/# ibooks: http://vocabulary.itunes.apple.com/rdf/ibooks/vocabulary-extensions-1.0/" xmlns="http://www.idpf.org/2007/opf">
<metadata xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:opf="http://www.idpf.org/2007/opf">
    <meta property="ibooks:specified-fonts">true</meta>
    <dc:title>{book['title']}</dc:title>
    <dc:identifier>urn:uuid:{book_uuid}</dc:identifier>
    <dc:creator id="cre">{book['author']}</dc:creator>
    <meta name="dtb:uuid" content="{book_uuid}"/>
    <meta refines="#cre" property="role" scheme="marc:relators">aut</meta>
    <dc:date>{datetime.now()}</dc:date>
    <dc:language>pt-BR</dc:language>
    <meta property="dcterms:modified">2023-11-01T16:29:53Z</meta>
    <meta property="rendition:orientation">portrait</meta>
    <meta name="generator" content="Meu Novo Livro" />
    <meta name="cover" content="cover.jpeg" />
</metadata>
<manifest>
    <item id="titlepage" href="titlepage.xhtml" media-type="application/xhtml+xml"/>
    <item id="cover" href="cover.jpeg" media-type="image/jpeg"/>
    <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
    {''.join(str(cap) for cap in item_list)}
    <item id="page_styles.css" href="page_styles.css" media-type="text/css"/>
    <item id="stylesheet.css" href="stylesheet.css" media-type="text/css"/>
    <item id="nav_styles.css" href="nav_styles.css" media-type="text/css"/>
    <item id="title_page_style.css" href="title_page_style.css" media-type="text/css"/>
    <item id="nav.xhtml" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>
    <item id="Bitter-Regular.ttf" href="Fonts/Bitter-Regular.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Bold.ttf" href="Fonts/Bitter-Bold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Italic.ttf" href="Fonts/Bitter-Italic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-BoldItalic.ttf" href="Fonts/Bitter-BoldItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Light.ttf" href="Fonts/Bitter-Light.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-LightItalic.ttf" href="Fonts/Bitter-LightItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Medium.ttf" href="Fonts/Bitter-Medium.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-MediumItalic.ttf" href="Fonts/Bitter-MediumItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-SemiBold.ttf" href="Fonts/Bitter-SemiBold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-SemiBoldItalic.ttf" href="Fonts/Bitter-SemiBoldItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-ExtraBold.ttf" href="Fonts/Bitter-ExtraBold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-ExtraBoldItalic.ttf" href="Fonts/Bitter-ExtraBoldItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Black.ttf" href="Fonts/Bitter-Black.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-BlackItalic.ttf" href="Fonts/Bitter-BlackItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-ExtraLight.ttf" href="Fonts/Bitter-ExtraLight.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-ExtraLightItalic.ttf" href="Fonts/Bitter-ExtraLightItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Thin.ttf" href="Fonts/Bitter-Thin.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-ThinItalic.ttf" href="Fonts/Bitter-ThinItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Regular.ttf" href="Fonts/WorkSans-Regular.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Bold.ttf" href="Fonts/WorkSans-Bold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Italic.ttf" href="Fonts/WorkSans-Italic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-BoldItalic.ttf" href="Fonts/WorkSans-BoldItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Light.ttf" href="Fonts/WorkSans-Light.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-LightItalic.ttf" href="Fonts/WorkSans-LightItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Medium.ttf" href="Fonts/WorkSans-Medium.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-MediumItalic.ttf" href="Fonts/WorkSans-MediumItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-SemiBold.ttf" href="Fonts/WorkSans-SemiBold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-SemiBoldItalic.ttf" href="Fonts/WorkSans-SemiBoldItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-ExtraBold.ttf" href="Fonts/WorkSans-ExtraBold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-ExtraBoldItalic.ttf" href="Fonts/WorkSans-ExtraBoldItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-ExtraLight.ttf" href="Fonts/WorkSans-ExtraLight.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-ExtraLightItalic.ttf" href="Fonts/WorkSans-ExtraLightItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Thin.ttf" href="Fonts/WorkSans-Thin.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-ThinItalic.ttf" href="Fonts/WorkSans-ThinItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Black.ttf" href="Fonts/WorkSans-Black.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-BlackItalic.ttf" href="Fonts/WorkSans-BlackItalic.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="DancingScript-Regular.ttf" href="Fonts/DancingScript-Regular.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="DancingScript-Bold.ttf" href="Fonts/DancingScript-Bold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="DancingScript-Medium.ttf" href="Fonts/DancingScript-Medium.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="DancingScript-SemiBold.ttf" href="Fonts/DancingScript-SemiBold.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="DancingScript-VariableFont_wght.ttf" href="Fonts/DancingScript-VariableFont_wght.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-Italic-VariableFont_wght.ttf" href="Fonts/Bitter-Italic-VariableFont_wght.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="Bitter-VariableFont_wght.ttf" href="Fonts/Bitter-VariableFont_wght.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-VariableFont_wght.ttf" href="Fonts/WorkSans-VariableFont_wght.ttf" media-type="application/vnd.ms-opentype"/>
    <item id="WorkSans-Italic-VariableFont_wght.ttf" href="Fonts/WorkSans-Italic-VariableFont_wght.ttf" media-type="application/vnd.ms-opentype"/>
</manifest>
<spine toc="ncx">
    <itemref idref="nav.xhtml" linear="no"/>
    {''.join(str(cap) for cap in item_ref_list)}
</spine>
</package>"""
        Path(f'{book_path}/content.opf').touch()
        with open(f'{book_path}/content.opf', 'w') as f:
            f.write(meta)

        shutil.copy(
            f'media/books/{book['name']}/cover.jpeg',
            f'{book_path}/cover.jpeg')

        shutil.make_archive(f'{book_path}', 'zip', f'{book_path}')
        epub = Path(f'{book_path}.zip')
        epub = epub.rename(epub.with_suffix('.epub'))
        return epub

    def get(self, request, *args, **kwargs):
        id = kwargs['id']
        book = self.get_object(id, request)
        book_serializer = GetOneBookSerializer(book)
        book_data = book_serializer.data
        epub = self.generate_epub(book_data)

        shutil.rmtree(f'bookGen/{book_data['name']}')

        path = 'tmp'
        if not os.path.exists(path):
            os.mkdir(path)

        book_path = f'{path}/{book_data['name']}'
        if not os.path.exists(book_path):
            os.mkdir(book_path)

        shutil.copy(epub, book_path)

        os.remove(f'bookGen/{book_data['name']}.epub')

        render_str = f'''<div><img src="http://127.0.0.1:8000/{
            book_data["cover"]}" class="cover"/> </div>{
            book_data['content']}'''

        pdfkit.from_string(
            render_str, f'{book_path}/{book_data['name']}.pdf',
            css='books/style.css')

        zip = shutil.make_archive(f'{book_path}', 'zip', f'{book_path}')

        zip_to_download = open(zip, 'rb')

        response = HttpResponse(
            zip_to_download, content_type='''application/zip''')

        response['Content-Disposition'] = f'''attachment; filename={
            book_data['name']}.zip'''

        shutil.rmtree(book_path)
        os.remove(f'{path}/{book_data['name']}.zip')

        return response
