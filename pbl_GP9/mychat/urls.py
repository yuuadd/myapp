from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views  # ここはアプリ内なのでOK

app_name = 'mychat'

urlpatterns = [
    path('', views.startView, name='start'),
    path('signup/', views.createUser, name='signup'),
    path('login/', views.loginView, name='login'),
    path('main/', views.main, name='main'),
    path('map/', views.mapView, name='map'),
    path('recom/', views.recomView, name='recom'),
    path('search/', views.searchView, name='search'),
    path('post/', views.postView, name='post'),
    path('result/', views.resultView, name='result'),
    path('write/', views.writeView, name='write'),
    path('list/', views.postListView, name='list'),
    path('detail/<int:post_id>/', views.postDetailView, name='detail'),
    path('shop/<int:shop_id>/',views.shopDetailView, name='shop_detail'),
]