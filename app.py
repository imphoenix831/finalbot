# -*- coding: utf-8 -*-
"""
Created on Fri Aug 24 18:12:45 2018

@author: linzino
"""
# server-side
from flask import Flask, request, abort

# line-bot
from linebot import (LineBotApi, WebhookHandler)
from linebot.exceptions import (InvalidSignatureError)
from linebot.models import *

# package
import re
from datetime import datetime 

# customer module
import mongodb
import corwler


app = Flask(__name__)

line_bot_api = LineBotApi('qWzdizT942+Qj7WRypvh9m5diBU6o2G0gSNjiV7mw2tU468qos7YhvNOPhWsW7hJ7ETJxdzT1VFZ1l1lOpZZ+Yu40jKnRByD3A+R8OEkwYUtku+kbUeovNTZ30t49mpSLiQh/Xx9iZNALAy4IvqiEgdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('a2e7a0de8f5fe196808a893a40fe2607')



@app.route("/callback", methods=['POST'])
def callback():

    
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'


@handler.add(FollowEvent)
def handle_follow(event):
    '''
    當使用者加入時觸動
    '''
    # 取得使用者資料
    profile = line_bot_api.get_profile(event.source.user_id)
    name = profile.display_name
    uid = profile.user_id
    
    print(name)
    print(uid)
    # Udbddac07bac1811e17ffbbd9db459079
    if mongodb.find_user(uid,'users')<= 0:   ## <=0 表示找不到User 資料,則為新使用者
        # 整理資料
        dic = {'userid':uid,
               'username':name,
               'creattime':datetime.now(),
               'Note':'user',
               'ready':0}
        
        mongodb.insert_one(dic,'users')
   


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    '''
    當收到使用者訊息的時候
    '''
    profile = line_bot_api.get_profile(event.source.user_id)
    name = profile.display_name
    uid = profile.user_id
    message = event.message.text
    print(name)
    print(uid)
    print(message)
    
    dic = {'userid':uid,
       'username':name,
       'creattime':datetime.now(),
       'mess':message}
    mongodb.insert_one(dic,'message')
    
    if mongodb.get_ready(uid,'users') ==1 :
        mongodb.update_byid(uid,{'ready':0},'users')
        casttext = name+' 對大家說： '+message
        remessage = TextSendMessage(text=casttext)
        userids = mongodb.get_all_userid('users')
        line_bot_api.multicast(userids, remessage)
        return 0 
    
    if message == '群體廣播':
        # 設定使用者下一句話要群廣播
        mongodb.update_byid(uid,{'ready':1},'users')
        remessage = TextSendMessage(text='請問您要廣播什麼呢?')
        line_bot_api.reply_message(
                        event.reply_token,
                        remessage)
        return 0 
    
    if re.search('Hi|hello|你好|ha', message, re.IGNORECASE):
        line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
        
        return 0 
    

    if re.search('新聞|news', event.message.text, re.IGNORECASE):
        dic = corwler.udn_news()
        
        columns = []
        for i in range(0,3):
            carousel = CarouselColumn(
                        thumbnail_image_url = dic[i]['img'],
                        title = dic[i]['title'],
                        text = dic[i]['summary'],
                        actions=[
                            URITemplateAction(
                                label = '點我看新聞',
                                uri = dic[i]['link']
                              )
                            ]
                        )
            columns.append(carousel)
        
        remessage = TemplateSendMessage(
                    alt_text='Carousel template',
                    template=CarouselTemplate(columns=columns)
                    )
        
        
        line_bot_api.reply_message(event.reply_token, remessage)
        return 0 
        
    if re.search('Dcard|dcard', event.message.text, re.IGNORECASE):
        text = corwler.Dcard()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
        return 0 

    if re.search('Google|google', event.message.text, re.IGNORECASE):
        text = corwler.google_query()
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text))
        return 0 
        
   
    if message == 'googlemap':
        # 取得最新評價
        text = corwler.google()
        # 包裝訊息
        remessage = TextSendMessage(text=text)
        # 回應使用者
        line_bot_api.reply_message(
                        event.reply_token,
                        remessage)
        return 0 
    
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))
    return 0 


if __name__ == '__main__':
    app.run(debug=True)