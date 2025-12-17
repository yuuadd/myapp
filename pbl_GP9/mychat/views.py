from django.shortcuts import render, redirect
from .models import User, Room,Post,Shop
#検索用にモジュール追加
from django.db.models import Q


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


#ログイン投稿処理
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
    response.set_cookie('USER', user_name)
    return response


def main(request):
    return render(request, 'main.html')

def mapView(request):
    return render(request, 'map.html')

def recomView(request):
    return render(request, 'recom.html')

#検索機能の実装
def searchView(request):
    #検索ワードを取得する文字列。空白で区切る
    #おそらく大半の人は空白が全角スペースになると思うので、全角スペースも考慮
    raw = request.GET.get("search", "")   
    #例：「ラーメン　中島」⇒「ラーメン,中島」
    keyword = raw.replace("　", " ").strip().split()
   
    #検索ワードが含まれる投稿を取得
    #投稿がないい場合はメッセージ表示(html側で実装)
    posts = Post.objects.none()
    #店名、ジャンル、場所のいずれかに検索ワードが含まれれば良い
    if keyword:
        #条件をセット
        conditions = Q()
        #キーワードごとに条件に合致する店を創作
        for word in keyword:
            conditions |=(
            Q(shop_name__icontains=word) |
            Q(genre__icontains=word) |
            Q(location__icontains=word) |
            Q(menu__icontains=word)
            )
        posts = Post.objects.filter(conditions).order_by('-created')
            
    # 検索結果を表示
    #postは投稿一覧、qは検索ワード
    print("検索ワード:", keyword)
    print("全投稿:", list(Post.objects.values()))
    return render(request, 'search.html', {
        "posts": posts,
        "q":keyword,
        })

def postView(request):
    return render(request, 'post.html')

#
def resultView(request):
    if request.method == "POST":
        shop_name = request.POST.get('shop_name')
        genre = request.POST.get('genre')
        location = request.POST.get('location', '')
        photo = request.FILES.get('photo')
        menu = request.POST.get('menu')

        user_name = request.COOKIES.get('USER')
        user_obj = User.objects.filter(name=user_name).first() if user_name else None

        Post.objects.create(
            user=user_obj,
            shop_name=shop_name,
            genre=genre,
            location=location,
            photo=photo,
            menu=menu,
        )

        return redirect('mychat:list')

    return redirect('mychat:write')

# 投稿編集画面表示
def writeView(request):
    # shop表示用の初期データ
    initial_shops = [
        {"name": "サイノ", "genre": "カレー", "location": "室蘭", "rest": "不定休", "time": "11時00分~15時00分,17時00分~22時00分", "tel":"0143-83-6298"},
        {"name": "アスコット", "genre": "レストラン", "location": "室蘭", "rest": "木曜日", "time": "11時30分~14時30分,17時30分~20時30分", "tel": "0143-44-1560"},
        {"name": "一平", "genre": "焼き鳥", "location": "室蘭", "rest": "不定休", "time": "11時00分~14時00分,17時00分~22時00分", "tel": "0143-41-0550"},
        
    ]
    for shop in initial_shops:
        if not Shop.objects.filter(name=shop["name"]).exists():
            Shop.objects.create(**shop)

    shops = list(Shop.objects.all().values("name", "genre", "location","rest","time","tel"))
    
    back_to = request.GET.get("from", "main")
    return render(request, "write.html", {
        "shops": shops,
        "back_to": back_to,
    })


# 投稿一覧表示用画面
def postListView(request):
    posts = Post.objects.order_by('-created')  # 新しい順に並べる
    return render(request, 'post_list.html', {"posts": posts})


# 投稿された店の詳細を表示する
def postDetailView(request, post_id):
    post = Post.objects.get(id=post_id)
    shop = Shop.objects.filter(name=post.shop_name).first()

    return render(request, 'post_detail.html', {
        "post": post,
        "shop": shop,
    })

