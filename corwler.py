# -*- coding: utf-8 -*-
"""
Created on Sat Aug 25 00:17:32 2018

@author: linzino
"""
import requests #引入函式庫
from bs4 import BeautifulSoup
import re
import json
import feedparser


def udn_news():
    '''
    抓最新前三篇新聞
    
    回傳是一個dict
    '''
    # rss_url = 'https://udn.com/rssfeed/news/2/6638?ch=news'
    #rss_url = 'https://tw.appledaily.com/rss/newcreate/kind/rnews/type/106'
    rss_url ='https://www.bnext.com.tw/rss'
 
    # 抓取資料
    rss = feedparser.parse(rss_url)
    
    cards = []    
    for index in range(0,3):
        # 抓文章標題
        title = rss['entries'][index]['title']
        # 抓文章連結
        link = rss['entries'][index]['link']
        # 處理摘要格式
        summary =  rss['entries'][index]['summary']
        
        if 'img' in summary:
            soup = BeautifulSoup(summary, 'html.parser')
            p_list = soup.find_all('p')
            # 抓文章摘要 限制只有60個字
            text = p_list[1].getText()[:50]
            # 抓文章圖片
            image = p_list[0].img['src']
        else:
            # 沒有圖片
            text = summary[:50]
            image = 'https://i.imgur.com/vkqbLnz.png'
        
        card = {'title':title,
                'link':link,
                'summary': text,
                'img':image
                }
        cards.append(card)
        
    return cards


def google():
    '''
    抓到最新google map資料
    '''
    pretext = ')]}\''
    
    # 爬下com
    url = 'https://www.google.com.tw/maps/preview/reviews?authuser=0&hl=zh-TW&gl=tw&pb=!1s0x3442abcfe9e7617d%3A0x496596e7748a5757!2i0!3i10!4e3!7m4!2b1!3b1!5b1!6b1'
    #url = 'https://www.google.com/maps/preview/reviews?authuser=0&hl=zh-TW&gl=tw&pb=!1s0x3442a98bd9f5f4e9%3A0x2c7ce8f62da01bc6!2i8!3i10!4e6!5m2!1sGVnmW5HKMsX78QWJrp_wDA!7e81!7m4!2b1!3b1!5b1!6b1'
    resp = requests.get(url)
    text = resp.text.replace(pretext,'')
    soup = json.loads(text)
    
    # 抓第一篇
    first = soup[0][0]
    # 整理資料 
    username = first[0][1]
    time = first[1]
    mesg = first[3]
    star = first[4]
    
    string = '%s \n於 %s 將您評為 %s顆星 \n留言：%s' % (username, time,star,mesg)
    
    return string

def Dcard():
    '''
    在Dcard 上某個關鍵字最新的文章
    '''
    url = 'https://www.dcard.tw/f'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    atags = soup.find_all('a', re.compile('PostEntry_root_'))
    
    pre_url = 'https://www.dcard.tw/'
    
    string = '最新4篇Dcard貼文：\n'
    for  item in atags[:4]:
        string += pre_url+item['href']+'\n'
    
    return string
    
def google_query(message):
    google_url = 'https://www.google.com.tw/search'
    # 查詢參數
    my_params = {'q': message}

    # 下載 Google 搜尋結果
    r = requests.get(google_url, params = my_params)
    # 確認是否下載成功
    if r.status_code == requests.codes.ok:
        # 以 BeautifulSoup 解析 HTML 原始碼
        soup = BeautifulSoup(r.text, 'html.parser')

          # 觀察 HTML 原始碼
          # print(soup.prettify())

          # 以 CSS 的選擇器來抓取 Google 的搜尋結果
        items = soup.select('div.g > h3.r > a[href^="/url"]')           
        string = '最新 2 篇 google貼文：\n'
        for  item in items[:2]:
            #print("標題：" + i.text)
            text = item['href'].replace('/url?q=','')
            string += text+'\n'
    
        return string    
    
