from rest_framework import serializers
from .models import Book


class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ('__all__')


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
