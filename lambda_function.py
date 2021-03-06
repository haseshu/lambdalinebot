import os
import sys
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,LocationMessage
)
from linebot.exceptions import (
    LineBotApiError, InvalidSignatureError
)
import logging
import random
import sys
import urllib.parse
import urllib.request
import requests
import json
import boto3
import xmltodict

logger = logging.getLogger()
logger.setLevel(logging.ERROR)

#天気ここから
class Weather:
    WEATHER_URL="http://weather.livedoor.com/forecast/webservice/json/v1?city=%s"
    CITY_CODE="130010" # TOKYO


    def get_weather_info(self):
        try:
            url = "http://weather.livedoor.com/forecast/webservice/json/v1?city=130010"
            html = urllib.request.urlopen(url)
            html_json = json.loads(html.read().decode('utf-8'))

		#この辺りが上手くいっていない
        except Exception as e:
            print ("Exception Error: ", e)
            sys.exit(2)
        return html_json

    def set_weather_info(self,weather_json, day,describe):
        max_temperature = 'None'
        min_temperature = 'None'
        date_Label = day
        #print(weather_json)
        try:
            descript = weather_json['description']['text']
            for forecast in weather_json['forecasts']:
                #print(forecast['dateLabel'])
                if forecast['dateLabel'] == date_Label:
                    #print(forecast['temperature']['max']['celsius'])
                    date = forecast['date']
                    weather = forecast['telop']
                    if forecast['temperature']['max'] is not None:
                        max_temperature = forecast['temperature']['max']['celsius']
                    if  forecast['temperature']['min'] is not None:
                        min_temperature = forecast['temperature']['min']['celsius']

        except TypeError:
        # temperature data is None etc...
            date = "error"
            weather = "error"
            max_temperature = "error"
            min_temperature = "error"
        #print(date+"\n"+weather + "\nmin:" + min_temperature + "\nmax:" + max_temperature)
        if describe == True:
            msg = date + "\nweather:" + weather + "\nmin:" + min_temperature + "\nmax:" + max_temperature + "\ndescript:" + descript
        else:
            msg = date + "\nweather:" + weather + "\nmin:" + min_temperature + "\nmax:" + max_temperature
        return msg

    def day_check(self,days):
        dateLabel = "明日"
        #print(days)
        if days == 0:
            dateLabel = "今日"
        elif days == 1:
            dateLabel = "明日"
        elif days == 2:
            dateLabel = "明後日"
        return dateLabel

    def wheter_news(self,day,describe):
        kekka_html = self.get_weather_info()
        #print(self.kekka_html)
        day_label = self.day_check(day)
        print("day_label="+day_label)
        self.news = self.set_weather_info(kekka_html,day_label,describe)
        return self.news


#じゃんけんここから

class Janken:

	def Server_te(self):
		self.server = random.randint(0,2)
		return self.server

	def Client_te(self,client_te):
		if client_te == 'グー':
			self.client = 0
		elif client_te == 'チョキ':
			self.client = 1
		elif client_te == 'パー':
			self.client = 2
		else:
			 self.client =9
		return self.client

	def Janken(self,client_te):
		server = self.Server_te()
		client = self.Client_te(client_te)
		print(server)
		print(client)
		if client==9:
			print("グー、チョキ、パーのいずれかを入力してください")
			kekka = "グー、チョキ、パーのいずれかを入力してください"
		elif server==client:#引き分けの場合
			print("引き分け")
			kekka="引き分け"
		elif server==0:#サーバがグーの時
			if client==1:
				print("負け")
				kekka = "ぼくはグー\n君の負け"
			if client==2:
				print("勝ち")
				kekka = "ぼくはグー\n君の勝ち"
		elif server==1:#サーバがチョキの時
			if client==0:
				print("勝ち")
				kekka = "ぼくはチョキ\n君の勝ち"
			if client==2:
				print("負け")
				kekka = "ぼくはチョキ\n君の負け"
		elif server==2:#サーバがパーの時
			if client==0:
				print("負け")
				kekka = "ぼくはパー\n君の負け"
			if client==1:
				print("勝ち")
				kekka = "ぼくはパー\n君の勝ち"
		return kekka

#位置情報から最寄りの駅を割り出して送信する
class Location:
    #simpleapi利用例
    #http://map.simpleapi.net/stationmap?x=139.75271700&y=35.70481800
    SIMPLE_API_URL="http://map.simpleapi.net/stationapi?"
    #現在地から駅の場所を送信するメイン
    def LocationToStation(self,latitude,longitude):
        print("現在地から駅の場所を送信するメイン")
        station_xml = self.Get_Station_Info(latitude,longitude)

        for station_list in station_xml['result']:
            print("駅")
            print(station_list)

        return self.LineBot_Result(station_list)

    def Get_Station_Info(self,latitude,longitude):
        try:
            url = Location.SIMPLE_API_URL + "x=" + str(latitude) + "&y=" + str(longitude)+"&output=json"
            html = urllib.request.urlopen(url)
            print(html)
            print(html.read())
            html_json = json.loads(html.read())
            print(html_json)

        except Exception as e:
            print ("Exception Error: ", e)
            sys.exit(2)
        return html_json

    def LineBot_Result(self,xml):

        return json.dumps(xml)

#英和翻訳ここから
class TransLater:
    TRANSLATE_URL="https://script.google.com/macros/s/AKfycbz3OSPifvcoGNeO4RcoU59DZxcRfK6u4QuRKGiTHtWflNsEtX-a/exec?text="
    SOURCE="&source="
    TARGET="&target="

#もし翻訳なら、ここに記載する
#https://script.google.com/macros/s/AKfycbweJFfBqKUs5gGNnkV2xwTZtZPptI6ebEhcCU2_JvOmHwM2TCk/exec?text=こんにちわ&source=ja&target=en
    def Translater_Japanese_To_English(self,Japanese):
        url = TransLater.TRANSLATE_URL + Japanese + TransLater.SOURCE + "ja" + TransLater.TARGET + "en"
        print(url)
        html = requests.get(url)
        print(html)
        print(html.text)
        return html.text

    def Translater_English_To_Japanese(self,English):
        url = TransLater.TRANSLATE_URL + English + TransLater.SOURCE + "en" + TransLater.TARGET + "ja"
        print(url)
        html = requests.get(url)
        print(html)
        print(html.text)
        return html.text


#おうむ返しここから
channel_secret = os.getenv('LINE_CHANNEL_SECRET', None)
channel_access_token = os.getenv('LINE_CHANNEL_ACCESS_TOKEN', None)
if channel_secret is None:
    logger.error('Specify LINE_CHANNEL_SECRET as environment variable.')
    sys.exit(1)
if channel_access_token is None:
    logger.error('Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.')
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
handler = WebhookHandler(channel_secret)


def lambda_handler(event, context):
    signature = event["headers"]["X-Line-Signature"]
    body = event["body"]
    ok_json = {"isBase64Encoded": False,
               "statusCode": 200,
               "headers": {},
               "body": ""}
    error_json = {"isBase64Encoded": False,
                  "statusCode": 403,
                  "headers": {},
                  "body": "Error"}

    @handler.add(MessageEvent, message=TextMessage)
    def message(line_event):

        text = line_event.message.text
        text_kekka = text
	#じゃんけんかどうか判断
	#じゃんけんなら、textの中身をじゃんけんの結果に置き換える
        a = Janken()
        if a.Client_te(text) != 9:
            kekka = a.Janken(text)
            text_kekka = kekka

    #翻訳かどうかチェック
    #頭に"翻訳"とあれば日本語→英語、頭に"Translate"とあれば英語→日本語
        if text.startswith("翻訳"):
            t= TransLater()
            text_trans=text[len("翻訳"):]
            print(text_trans)
            text_kekka = t.Translater_Japanese_To_English(text_trans)
        elif text.startswith("Translate"):
            t= TransLater()
            text_trans=text[len("Translate"):]
            print(text_trans)
            text_kekka = t.Translater_English_To_Japanese(text_trans)


        #天気かどうか判断
        #天気なら、textの中身を天気の結果に置き換える
        elif "天気" in text:
            day = 0
            describe = False
            if "今日" in text:
                day = 0
            if "明日" in text:
                day = 1
            if "明後日" in text:
                day = 2
            if "詳細" in text:
                describe = True
            tenki = Weather()
            text_kekka =  tenki.wheter_news(day,describe)

        #予定の文字があればGoogleCalendarLamndaへ連携
        elif "予定" in text:
            clientLambda = boto3.client("lambda")
            params = {"body" : text}
            print("予定ここから")
            res = clientLambda.invoke(
                FunctionName="LambdaGoogleCalender",
                InvocationType="RequestResponse",
                Payload=json.dumps(params)
            )
            text_kekka=json.loads(res['Payload'].read())
            text_kekka=text_kekka["body"]

        print(text_kekka)
        line_bot_api.reply_message(line_event.reply_token, TextSendMessage(text=text_kekka))

    #位置情報の時に使う
    @handler.add(MessageEvent, message=LocationMessage)
    def location(line_event):
        #位置情報が来ていれば、simpleapiにつなぐ
        if line_event.message.type == "location":
            latitude =line_event.message.latitude #緯度
            longitude=line_event.message.longitude #経度
            station =Location()
            station.LocationToStation(latitude,longitude)


    try:
        handler.handle(body, signature)
    except LineBotApiError as e:
        logger.error("Got exception from LINE Messaging API: %s\n" % e.message)
        for m in e.error.details:
            logger.error("  %s: %s" % (m.property, m.message))
        return error_json
    except InvalidSignatureError:
        return error_json

    return ok_json
