# -*- coding: utf-8 -*-

# some settings

import os

# headers
HEADERS = {
    #"Connection": "keep-alive",
    "Origin": "https://www.bilibili.com",
    #"Host": "www.bilibili.com",
    "User-Agent": "",
}

USERA_GENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36"
]


# maximum concurrent threads
CONCURRENT_REQUESTS = 16

# a delay for download
DOWNLOAD_TIMEOUT = 300

# crawl informations

ITEM = {
    "description" : "",
    "author": "",
    "av": "",
    "coverImage": "",
    "title": "",
    "name": "",
    "extraName": "",
    "pageInfo": "",
    "page": "",
    "videoDownloadUrl": "",
    "audioDownloadUrl": "",
    "referer" :""
}

# download path

FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'Video'
)
