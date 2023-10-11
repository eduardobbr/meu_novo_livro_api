from django.db import models

class Book(models.Model):
    def upload_page_name(self, filename):
        return f'books/{self.name}_{self.author}/{filename}'
    
    BOOK_STYLE_CHOICES = ['classic','modern']

    name: models.CharField(max_length=50)
    content: models.TextField()
    synopsis: models.TextField()
    value: models.FloatField()
    production: models.BooleanField(default=True)
    cover: models.ImageField(upload_to=upload_page_name)
    title: models.CharField(max_length=50)
    subtitle: models.CharField(max_length=50)
    author: models.CharField(max_length=50)
    isbn: models.CharField(max_length=13)
    public_target: models.IntegerField(2)
    keywords: models.TextField()
    book_style: models.CharField(choices=BOOK_STYLE_CHOICES)
    price: models.FloatField()
    user: models.ManyToManyField("User")
 
    def __str__(self):
        return self.name