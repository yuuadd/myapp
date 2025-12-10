from django.shortcuts import render, redirect
from .models import User, Room
from .models import Post
from .models import Shop
import urllib.parse


def startView(request):
    return render(request, 'start.html')


#ユーザ登録処理
def createUser(request):
    error_messages = []

    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        password = request.POST.get("password", "").strip()
        password_confirm = request.POST.get("password_confirm", "").strip()

        # 入力
        if not name:
            error_messages.append("ユーザ名が未記入です。")
        if not password:
            error_messages.append("パスワードが未記入です。")
        if password != password_confirm:
            error_messages.append("パスワードが一致しません。")  # 再入力

        # ユーザ登録処理
        if not error_messages:
            try:
                existing_user = User.objects.get(name=name)
                error_messages.append("すでにそのユーザは存在します。")
            except User.DoesNotExist:
                new_user = User(name=name, password=password)
                new_user.save()
                return redirect('mychat:start')

    # エラーがあれば同じ登録画面に戻す
    context = {
        "error_messages": error_messages,
    }
    return render(request, "signup.html", context)


#ログイン処理を行う関数
def loginView(request):
    error_messages = []

    #クッキーからユーザ名を取得
    cookie_user = request.COOKIES.get('USER')
    if cookie_user:
        try:
            user_obj = User.objects.get(name=cookie_user)
            if user_obj.islogin:
                #   ログイン中ならメイン画面へ
                response = redirect('mychat:main')
                return response
            else:
                #   ログイン状態 False の場合クッキー削除
                response = redirect('mychat:login')
                response.delete_cookie('USER')
                return response
        except User.DoesNotExist:
            response = redirect('mychat:login')
            response.delete_cookie('USER')
            return response

    #フォームデータ取得
    user_name = request.POST.get('name', '').strip()
    password = request.POST.get('password', '').strip()
    login_flag = request.POST.get('login', 'off')

    #ログインフラグが on でない場合、ログイン画面に戻る
    if login_flag != "on":
        return render(request, "login.html")

    #入力チェック
    if not user_name:
        error_messages.append("ユーザ名が入力されていません")
    if not password:
        error_messages.append("パスワードが入力されていません")

    #入力エラーがある場合
    if error_messages:
        return render(request, "login.html", {'error_messages': error_messages})

    #データベースから一致するユーザ情報を取得
    try:
        user_obj = User.objects.get(name=user_name, password=password)
    except User.DoesNotExist:
        #一致しない場合
        error_messages.append("ユーザ名、パスワードが一致しません")
        return render(request, "login.html", {'error_messages': error_messages})

    #ログイン状態を True に更新
    user_obj.islogin = True
    user_obj.save()

    #クッキーにユーザ名を設定してメイン画面へ
    response = redirect('mychat:main')
    response.set_cookie('USER', urllib.parse.quote(user_name))
    return response

def main(request):
    return render(request, 'main.html')

def mapView(request):
    return render(request, 'map.html')

def recomView(request):
    return render(request, 'recom.html')

def searchView(request):
    return render(request, 'search.html')

# views.py
def postView(request):
    # 初期データを直接追加（存在チェックあり）
    initial_shops = [
        {"name": "赤坂ラーメン", "genre": "ラーメン", "location": "東京都港区赤坂"},
        {"name": "新宿カフェ", "genre": "カフェ", "location": "東京都新宿区"},
        {"name": "渋谷寿司", "genre": "寿司", "location": "東京都渋谷区"},
    ]

    for shop in initial_shops:
        if not Shop.objects.filter(name=shop["name"]).exists():
            Shop.objects.create(**shop)

    shops = Shop.objects.all()
    back_to = request.GET.get("from", "main")
    return render(request, "write.html", {
        "shops": shops,
        "back_to": back_to,
    })

def resultView(request):
    if request.method == "POST":
        shop_name = request.POST.get('shop_name')
        genre = request.POST.get('genre')
        location = request.POST.get('location')
        photo = request.FILES.get('photo')  # ←ここ重要
        menu = request.POST.get('menu')
        visited_date = request.POST.get('visited_date')

        user_name = request.COOKIES.get('USER')
        user_obj = None
        if user_name:
            try:
                user_obj = User.objects.get(name=user_name)
            except User.DoesNotExist:
                pass

        post = Post.objects.create(
            user=user_obj,
            shop_name=shop_name,
            genre=genre,
            location=location,
            photo=photo,
            menu=menu,
            visited_date=visited_date if visited_date else None
        )

        return render(request, 'result.html', {'post': post})

    return redirect('mychat:result')

def writeView(request):
    # ここでも初期データ追加して shops 取得する必要がある
    initial_shops = [
        {"name": "赤坂ラーメン", "genre": "ラーメン", "location": "東京都港区赤坂"},
        {"name": "新宿カフェ", "genre": "カフェ", "location": "東京都新宿区"},
        {"name": "渋谷寿司", "genre": "寿司", "location": "東京都渋谷区"},
    ]
    for shop in initial_shops:
        if not Shop.objects.filter(name=shop["name"]).exists():
            Shop.objects.create(**shop)

    shops = list(Shop.objects.all().values("name", "genre", "location"))
    
    back_to = request.GET.get("from", "main")
    return render(request, "write.html", {
        "shops": shops,
        "back_to": back_to,
    })

def postListView(request):
    posts = Post.objects.order_by('-created')  # 新しい順に並べる
    return render(request, 'post_list.html', {"posts": posts})

def postDetailView(request, post_id):
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return redirect('mychat:list')  # 無ければ一覧へ戻す

    return render(request, 'post_detail.html', {"post": post})
