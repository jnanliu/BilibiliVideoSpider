# -*- coding: utf-8 -*-
import os
import re
import time
import random
import json
import requests
from copy import deepcopy
from lxml import etree
from tqdm import tqdm
from pprint import pprint

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

from .settings import HEADERS, USERA_GENTS, ITEM

class Spider() :

    def __init__(self, mode, number, type) :

        self.mode = mode
        self.type = type
        self.number = number
        if mode == 'up' :
            self.start_url = 'https://space.bilibili.com/{}/video'.format(number)
        else :
            self.start_url = 'https://www.bilibili.com/video/av{}'.format(number)
        self.session = requests.Session()

    def parse(self) :

        if self.mode == 'up' :
            pageInfoUrl = 'https://space.bilibili.com/ajax/member/getSubmitVideos' +\
                '?mid={}&pagesize=30&tid=0&page=1&keyword=&order=pubdate'.format(self.number)
            response = self.request(pageInfoUrl, refer={'Referer': self.start_url})
            selector = json.loads(response.text,encoding='utf-8')
            totalPage = selector['data']['count']
            if totalPage == 0 :
                #print("这个up主还没有发布过视频...")
                yield None
            else :
                upInfoUrl = 'https://api.bilibili.com/x/space/acc/info?mid={}&jsonp=jsonp'.format(self.number)
                response = self.request(upInfoUrl, refer={'Referer': self.start_url})
                selector = json.loads(response.text, encoding='utf-8')
                upName = selector['data']['name']
                upFace = selector['data']['face']
                upSign = selector['data']['sign']
                for i in range(1, int(totalPage / 30 + 0.5) + 1) :
                    pageInfoUrl = 'https://space.bilibili.com/ajax/member/getSubmitVideos' +\
                        '?mid={}&pagesize=30&tid=0&page={}&keyword=&order=pubdate'.format(self.number, i)
                    response = self.request(pageInfoUrl, refer={'Referer': self.start_url})
                    selector = json.loads(response.text, encoding='utf-8')
                    videoList = selector['data']['vlist']
                    for idx, video in enumerate(videoList) :
                        video.update({
                            "upName" : upName,
                            "upFace" : upFace,
                            "upSign" : upSign,
                            "index" : (i - 1) * 30 + idx,
                            "total" : totalPage - 1
                        })
                        yield video
                        #yield from self.parseByAv(
                        #    'https://www.bilibili.com/video/av{}'.format(video['aid'])
                        #)
        else :
            yield from self.parseByAv(self.start_url)

    def parseByAv(self, url) :

        response = self.request(url, None)
        selector = etree.HTML(response.text)
        item = ITEM     
        item['title'] = selector.xpath('//title/text()')[0]
        item['description'] = selector.xpath('//meta[@name="description"]/@content')[0]
        item['author'] = selector.xpath('//meta[@name="author"]/@content')[0]
        item['av'] = re.compile(r'/av(\d+)').findall(url)[0]
        item['pageInfo'] = json.loads(
            '{' + re.compile(r'window.__INITIAL_STATE__=\{(.*?)\}\;').findall(response.text)[0] + '}'
        )['videoData']['pages']
        for page in item['pageInfo'] : 
            next_url = url + '/?p={}'.format(page['page'])
            item['name'] = page['part']
            item['page'] = page['page']
            item['referer'] = {"Referer" : next_url}
            yield from self.downloadUrlParse(next_url, deepcopy(item))

    def downloadUrlParse(self, url, Item) :

        response = self.request(url, None)
        selector = etree.HTML(response.text)
        item = Item
        playInfo = json.loads(
            '{' + re.compile(r'window.__playinfo__={(.*?)}<\/').findall(response.text)[0] + '}',
            encoding='utf-8'
        )['data']
        item['coverImage'] = selector.xpath('//meta[@itemprop="image"]/@content')[0]
        try :
            item['videoDownloadUrl'] = playInfo['dash']['video'][min(self.type, len(playInfo['dash']['video']))]['base_url']
        except KeyError :
            item['videoDownloadUrl'] = [i['url'] for i in playInfo['durl']]
        try :
            item['audioDownloadUrl'] = playInfo['dash']['audio'][0]['baseUrl']
        except KeyError :
            item['audioDownloadUrl'] = None
        
        yield item

    def request(self, url, refer) :

        headers = HEADERS
        headers['User-Agent'] = random.choice(USERA_GENTS)
        if refer is not None :
            headers.update(refer)
        return requests.get(
            url=url,
            headers=headers
            , verify=False
        )