from django.shortcuts import render
from django.conf import settings
from django.http import HttpResponse,HttpResponseBadRequest,HttpResponseForbidden
from django.views.decorators.csrf import csrf_exempt

from linebot import LineBotApi,WebhookParser
from linebot.exceptions import InvalidSignatureError,LineBotApiError
from linebot.models import MessageEvent, TextSendMessage ,TextMessage
import json
import googlemaps
import random
from datetime import datetime


line_bot_api = LineBotApi(settings.LINE_CHANNEL_ACCESS_TOKEN)
parser = WebhookParser(settings.LINE_CHANNEL_SECRET)
#讀取setting裡的兩個金鑰

@csrf_exempt
def callback(request):
    if request.method == 'POST':
        signature = request.META['HTTP_X_LINE_SIGNATURE']
        body = request.body.decode('utf-8')

        try:
            events = parser.parse(body, signature)
        except InvalidSignatureError:
            return HttpResponseForbidden()
        except LineBotApiError:
            return HttpResponseBadRequest()

        ids = []
        stores_info = []
        choice = '小吃'
        gmaps = googlemaps.Client(key='AIzaSyD3bgEOAkulGGTWeUMQTafiFCLtPFJq1uU')    


        for event in events:
            if isinstance(event, MessageEvent):
                if isinstance(event.message, TextMessage):
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=event.message.text))
                else:
                    place = event.message.address
                    geocode_result = gmaps.geocode(place)
                    loc = geocode_result[0]['geometry']['location']
                    for store in gmaps.places_nearby(keyword=choice, location=loc, radius=1000)['results']:
                        ids.append(store['place_id'])
                    ids = list(ids)
                    for id in ids:
                        stores_info.append(gmaps.place(place_id=id,language='zh-TW')['result']['name'])
                    
                    line_bot_api.reply_message(event.reply_token,TextSendMessage(text=stores_info[random.randint(0,9)]))
                    ans = stores_info[random.randint(0,9)]
        return HttpResponse()
    else:
        return HttpResponseBadRequest()        



def callhtml(request):
    now=datetime.now().weekday()
    ids = []
    dict_line = {0:[],1:[],2:[],3:[]}
    dict_store = {'name':'','rank': '','far':'','time':''}
    choices = ['麵食', '飯類', '焗烤','早午餐']
    gmaps = googlemaps.Client(key='AIzaSyD3bgEOAkulGGTWeUMQTafiFCLtPFJq1uU')
    place = request.GET.get('liff.state', None)[3:]
    geocode_result = gmaps.geocode(place)
    loc = geocode_result[0]['geometry']['location']

    if datetime.now().hour > 15:
        choices[3] = '火鍋' 
    else:
        choices[3] = '早午餐' 
    # weight, f = get_weigth(event.source.user_id)
    for i in range(0, 4):
        cont=5
        for store in gmaps.places_nearby(keyword=choices[i], location=loc, radius=1000, open_now=True)['results']:
            if cont > 0 :
                dict_store = dict()
                name = gmaps.place(place_id=store['place_id'],language='zh-TW')['result']['name']
                if name.find(' ') != -1:
                    name = name[:name.find(' '):]
                if name.find('(') != -1:
                    name = name[:name.find('('):]
                dict_store['name'] = name
                dict_store['rank'] = store['rating']
                dict_store['far'] = gmaps.distance_matrix(origins=loc,destinations=store['geometry']['location'])['rows'][0]['elements'][0]['distance']['text']
                dict_store['time'] = gmaps.place(place_id=store['place_id'],language='zh-TW')['result']['opening_hours']['weekday_text'][now][5:]
                dict_store['url'] = gmaps.place(place_id=store['place_id'],language='zh-TW')['result']['url']
                phone = gmaps.place(place_id=store['place_id'],language='zh-TW')['result']['international_phone_number']
                phone=phone.replace(' ','-')
                dict_store['phone'] = 'tel:'+ phone
                dict_store['share'] = 'https://facebook.com/sharer/sharer.php?u='+dict_store['url']
                dict_line[i].append(dict_store)
                cont=cont-1
            else:
                break
    for j in range(0,5):
        for n in range(0,len(dict_line)):
            if j >= len(dict_line[n]):
                continue
            else:
                ids.append(dict_line[n][j])
    return render(request,"draw.html",locals())

        # f.write(str(weight))
    # except:
    #     errormessage = "(讀取錯誤!)"
    #     return HttpResponseBadRequest() 




# def get_weigth(id):
#     path = './ID' + str(id) + '.txt'
#     if os.path.isfile(path):
#         f = open(path, 'r')
#         weight = list()
#         for i in f.readline():
#             if i != ' ':
#                 weight.append(int(i))
#         f.close()
#         f = open(path, 'w')
#     else:
#         f = open(path, 'w')
#         weight = [5, 5, 5, 5, 5, 5]
#     return weight, f




# Create your views here.
