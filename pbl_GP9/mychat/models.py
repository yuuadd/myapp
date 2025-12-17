from django.db import models
from django.contrib.auth.models import User

class Room(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class User(models.Model):
    name = models.CharField(max_length=20)
    password = models.CharField(max_length=20)
    islogin = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shop_name = models.CharField(max_length=100)
    genre = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    menu = models.CharField(max_length=200, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.shop_name

class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    genre = models.CharField(max_length=100)
    location = models.CharField(max_length=200, blank=True, default="")
    rest = models.CharField(max_length=100, blank=True, default="")
    time = models.CharField(max_length=100, blank=True, default="")
    tel = models.CharField(max_length=100, blank=True, default="")

    def __str__(self):
        return self.name
