from django.db import models


# Create your models here.
class GuestBook(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    contents = models.TextField()
    regdate = models.DateTimeField(auto_now=True)