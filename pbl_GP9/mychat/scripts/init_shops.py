# mychat/scripts/init_shops.py
import os
import sys
import django

# プロジェクトルートをパスに追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# settings モジュールを設定
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "pbl_GP9.settings")
django.setup()

from mychat.models import Shop

# 登録したい店のデータ
shops = [
    {"name": "寿司太郎", "genre": "寿司", "location": "東京"},
    {"name": "ラーメン山田", "genre": "ラーメン", "location": "大阪"},
    {"name": "カフェ花子", "genre": "カフェ", "location": "名古屋"},
]

# 登録（すでに存在する場合はスキップ）
for s in shops:
    Shop.objects.get_or_create(**s)

print("初期データ登録完了")
