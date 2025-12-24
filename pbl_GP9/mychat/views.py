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
    
    # Shop表示用の初期データを作成
    initial_shops = [
        {"name": "竹よし ラーメンハウス",
         "genre": "ラーメン店、ランチ、ディナー",
         "location": "宮の森町3丁目9-4",
         "rest": "月曜日",
         "time": "11時00分~15時20分,17時00分~20時20分",
         "tel":"0143-47-2888"},
        
        {"name": "やきとりの一平 學亭",
         "genre": "焼き鳥店、ランチ、ディナー",
         "location": "高砂町5丁目6-17 コーポ5in 1F",
         "rest": "不定休",
         "time": "11時00分~14時00分,17時00分~22時00分",
         "tel": "0143-41-0550"},
        
        {"name": "焼肉徳寿 室蘭店",
         "genre": "焼肉店、ランチ、ディナー",
         "location": "中島本町1丁目6-3",
         "rest": "不定休",
         "time": "(日～金)11時00分~22時30分、(土)11時00分~23時00分",
         "tel": "0143-41-1129"},
        
    ]
    for shop in initial_shops:
        # データベースに店が存在しない場合のみ登録
        if not Shop.objects.filter(name=shop["name"]).exists():
            Shop.objects.create(**shop)
    
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

    # 登録されている店の一覧を取得
    shops = list(Shop.objects.all().values(
        "name", "genre", "location","rest","time","tel"
    ))
    
    # 戻り先URLを取得（デフォルトは'main'）
    back_to = request.GET.get("from", "main")
    return render(request, "write.html", {
        "shops": shops,
        "back_to": back_to,
    })


# 投稿一覧表示用画面
def postListView(request):
    posts = Post.objects.order_by('-created')  # 新しい順に並べる
    return render(request, 'post_list.html', {"posts": posts})


# 投稿された投稿の詳細を表示する
def postDetailView(request, post_id):
    # 投稿情報を取得
    post = Post.objects.get(id=post_id)
    # 投稿された店の詳細情報を取得
    shop = Shop.objects.filter(name=post.shop_name).first()

    return render(request, 'post_detail.html', {
        "post": post,
        "shop": shop,
    })

def shopDetailView(request, shop_id):
    # 店の詳細情報を取得
    shop = Shop.objects.get(id=shop_id)

    return render(request, 'shop_detail.html', {
        "shop": shop,
    })
