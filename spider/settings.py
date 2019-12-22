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
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/77.0.3865.90 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
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
