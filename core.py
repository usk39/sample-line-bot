from geopy.geocoders import Nominatim
import requests
import pprint
import re


def geocoding(place):
   geolocator = Nominatim(user_agent="my-application")
   location = geolocator.geocode(place, timeout=10)
   if location is None:
       return
   else:
       latitude = location.latitude
       longitude = location.longitude
       return latitude, longitude


def hotpepper(push_text):
   place_search = re.search('「(.+?)」', push_text)
   if place_search is None:
       return "・場所が入力されていません。鍵括弧「」内に場所を入力してください。"
   place = place_search.group(1)

   latitude, longitude = geocoding(place)

   genre_name = ["居酒屋", "ダイニングバー・バル", "創作料理", "和食", "洋食", "イタリアン・フレンチ", "中華", "焼肉", \
                 "韓国料理", "アジア・エスニック料理", "各国料理", "カラオケ・パーティ", "バー・カクテル", "ラーメン", \
                 "お好み焼き・もんじゃ", "カフェ・スイーツ", "その他グルメ"]
   genre_number = ["G001", "G002", "G003", "G004", "G005", "G006", "G007", "G008", "G017", "G009", "G010", "G011", \
                   "G012", "G013", "G016", "G014", "G015"]
   genre_dict = dict(zip(genre_name, genre_number))
   genre = [i for i in genre_name if i in push_text]

   if push_text == "ジャンル一覧":
       msg = "・以下のジャンルを正確に入力してください。\n"
       msg += "\n".join(genre_name)
       return msg

   budget_search = re.search('(\d{3,5})円', push_text)

   url = "https://webservice.recruit.co.jp/hotpepper/gourmet/v1/"
   params = {'key': '6cb4872b41f2afb5',
             'format': 'json',
             'lat': latitude,
             'lng': longitude,
             'range': '4',
             }

   if budget_search:
       budget = int(budget_search.group(1))
       budget_dict = {500: "B009", 1000: "B010", 1500: "B011", 2000: "B001", 3000: "B002", 4000: "B003", 5000: "B008" \
           , 7000: "B004", 10000: "B005", 15000: "B006", 20000: "B012", 30000: "B013"}
       for k, v in budget_dict.items():
           if budget <= k:
               budget_code = v
               break
       else:
           budget_code = "B014"  # 30001以上の場合
       params["budget"] = budget_code

   if genre:
       for x in genre:
           params.setdefault("genre", []).append(genre_dict[x])

   try:
       r = requests.get(url, params=params)
       content = r.json()

       if content["results"]["results_available"] == 0:
           return "ご指定の条件では見つかりませんでした。"
       num = content["results"]["results_returned"]

       content = content["results"]["shop"]

       msg = ""
       for shop in content:
           msg += shop["name"] + "("
           msg += shop["mobile_access"] + "): "
           msg += shop["urls"]["pc"] + "\n"

       msg = place + "の半径1km以内のお店を" + str(num) + "件表示します。\n" + msg
       return msg

   except:
       return "API接続中に何らかのエラーが発生しました"
