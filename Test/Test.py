#-*-coding:utf-8-*-

import requests, re, json
import parser
import urllib
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
from urllib.request import urlopen
import youtube_dl

def yt(name):
    url = "https://www.googleapis.com/youtube/v3/search"
    params = {
        'key' : '',
        'q' : name,
        'part' : 'snippet',
        'maxResults' : 5
        }

    html = requests.get(url, params=params).json()
    items = html['items']

    result = []

    for i in items:
        title = i['snippet']['title']
        tag = i['id']['videoId']

        result1 = {
            "title" : title,
            "tag" : tag
        }

        result.append(result1)

    return result

print(yt('Astronomia'))
