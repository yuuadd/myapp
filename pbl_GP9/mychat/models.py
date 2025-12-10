from django.db import models
from django.conf import settings



#
class Room(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

#ユーザのモデル
class User(models.Model):
    name = models.CharField(max_length=20, null=False, blank=False)
    password = models.CharField(max_length=20, null=False, blank=False)
    islogin = models.BooleanField(default=False)
    room = models.ForeignKey(Room, on_delete=models.CASCADE, null=True, blank=True)  # 部屋の紐付け（任意）

    def __str__(self):
        return self.name

#投稿のモデル
#名前、ジャンル、場所、写真、メニュー、訪問日、投稿日時
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    shop_name = models.CharField(max_length=100, blank=True, null=True)
    genre = models.CharField(max_length=100, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    photo = models.ImageField(upload_to='photos/', blank=True, null=True)
    menu = models.CharField(max_length=200, blank=True, null=True)
    visited_date = models.DateField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

# mychat/models.py
class Shop(models.Model):
    name = models.CharField(max_length=100, unique=True)
    genre = models.CharField(max_length=100)
    location = models.CharField(max_length=200)

    def __str__(self):
        return self.name
