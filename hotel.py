from geopy.geocoders import Nominatim
import requests
import re
import datetime

def geocoding(place):
   geolocator = Nominatim(user_agent="my-application")
   location = geolocator.geocode(place, timeout=10)
   if location is None:
       return
   else:
       latitude = location.latitude
       longitude = location.longitude
       return latitude, longitude

def hotel_search(place, checkin, checkout):
   latitude, longitude = geocoding(place)

   url = "https://app.rakuten.co.jp/services/api/Travel/VacantHotelSearch/20170426"
   params = {'applicationId': '1085028912694623115',
             'formatVersion': '2',
             'checkinDate': checkin,
             'checkoutDate': checkout,
             'latitude': latitude,
             'longitude': longitude,
             'searchRadius': '3',
             'datumType': '1',
             'hits': '30'}
   try:
       r = requests.get(url, params=params)
       content = r.json()
       error = content.get("error")
       if error is not None:
           msg = content["error_description"]
           return msg
       hotel_count = content["pagingInfo"]["recordCount"]
       hotel_count_display = content["pagingInfo"]["last"]
       msg = place + "の半径3km以内に合計" + str(hotel_count) + "件見つかりました。" + str(hotel_count_display) + "件を表示します。\n"
       for hotel in content["hotels"]:
           hotelname = hotel[0]["hotelBasicInfo"]["hotelName"]
           hotelurl = hotel[0]["hotelBasicInfo"]["hotelInformationUrl"]
           msg += "ホテル名:" + hotelname + ", URL:" + hotelurl + "\n"
       msg = msg.rstrip()
       return msg
   except:
       import traceback
       traceback.print_exc()
       return "API接続中に何らかのエラーが発生しました"

def extract_words(str):
   place_search = re.search('「(.+?)」', str)
   time_search = re.search(r'\d{4}/\d{1,2}/\d{1,2}', str)
   period_search = re.search('\D(\d{1,2})泊', str)
   error_msg = []
   if place_search is None:
       error_msg.append("・場所が入力されていません。鍵括弧「」内に場所を入力してください。")
   if time_search is None:
       error_msg.append("・チェックイン日が入力されていません。XXXX/XX/XXの形式で入力してください。")
   if period_search is None:
       error_msg.append("・宿泊日数が入力されていません。○○泊の形式で泊をつけて、半角数字(最大二桁)で入力してください。")
   if error_msg:
       error_msg = "\n".join(error_msg)
       return error_msg
   place = place_search.group(1)
   time = time_search.group()
   period = period_search.group(1)
   period = int(period)

   checkin = datetime.datetime.strptime(time, '%Y/%m/%d')
   checkout = checkin + datetime.timedelta(days=period)
   checkin = checkin.strftime("%Y-%m-%d")
   checkout = checkout.strftime("%Y-%m-%d")
   return place, checkin, checkout
