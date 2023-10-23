from django.db import models


class Book(models.Model):
    def upload_page_name(self, filename):
        return f'books/{self.name}_{self.author}/{filename}'
    BOOK_STYLE_CHOICES = (('M', 'modern'), ('C', 'classic'))

    name = models.CharField(max_length=50)
    content = models.TextField()
    synopsis = models.TextField()
    value = models.FloatField()
    production = models.BooleanField(default=True)
    cover = models.TextField()
    title = models.CharField(max_length=50)
    subtitle = models.CharField(max_length=50)
    author = models.CharField(max_length=50)
    isbn = models.CharField(max_length=13)
    public_target = models.IntegerField()
    keywords = models.TextField()
    book_style = models.CharField(choices=BOOK_STYLE_CHOICES, max_length=20)
    price = models.FloatField()
    user = models.ForeignKey(
        'users.User', on_delete=models.CASCADE, related_name="books")

    def __str__(self):
        return self.name
