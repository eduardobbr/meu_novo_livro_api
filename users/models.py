from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    phone = models.CharField(max_length=11)
    address = models.CharField(max_length=255)
    cpf = models.CharField(max_length=11)

    def __str__(self):
        return self.id
