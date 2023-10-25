from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.Serializer):
    name = serializers.CharField()
    content = serializers.CharField()
    synopsis = serializers.CharField()
    value = serializers.FloatField()
    production = serializers.BooleanField()
    cover = serializers.ImageField()
    title = serializers.CharField()
    subtitle = serializers.CharField()
    author = serializers.CharField()
    isbn = serializers.CharField()
    public_target = serializers.IntegerField()
    keywords = serializers.CharField()
    book_style = serializers.CharField()
    price = serializers.FloatField()


class GetAllBooksSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('id', 'name', 'synopsis', 'cover', 'title', 'subtitle',
                  'author', 'keywords', 'public_target', 'price', 'production',
                  'user')


class GetOneBookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('__all__')
