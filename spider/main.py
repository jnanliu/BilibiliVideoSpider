# -*- coding: utf-8 -*-
import os
import json
import time
import subprocess
import requests
import logging
from threading import Lock
from concurrent.futures import ThreadPoolExecutor, wait
from pyquery import PyQuery as pq
from download import Downloaer
from spider import Spider
from process import Process
from concatenate import VideoCat

from settings import CONCURRENT_REQUESTS

logger = logging.getLogger(__name__)
logger.setLevel(level = logging.INFO)
handler = logging.FileHandler("result.log")
handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

if __name__ == '__main__' :

    modes = ['av', 'up']
    mode = modes[int(input("请输入下载方式(以av号下载单个视频--0，下载UP主的所有投稿视频--1，输入对应的数字))："))]
    number = input("请输入av号或UP主的ID：")
    type = int(input("请输入下载画质(0为最高，数字越大画质越低)："))

    spider = Spider(mode, number, type)
    session = requests.Session()
    pool = ThreadPoolExecutor(max_workers=CONCURRENT_REQUESTS)
    startTime = time.time()
    for item in spider.parse() :

        process = Process(item)
        for (vPath, vUrl, aPath, aUrl, cUrl, cPath) in process() :
            videodownloader = Downloaer(vUrl, vPath, 1, 
                item['referer'],
                session
            )
            pool.submit(videodownloader, logger)
            if aUrl != None :
                audiodownloader = Downloaer(aUrl, aPath, 1, 
                    item['referer'],
                    session
                )
                pool.submit(audiodownloader, logger)
            with open(cPath, 'wb+') as f :
                f.write(requests.get(cUrl).content)
            time.sleep(2)
    pool.shutdown(wait=True)
    with open("result.log", 'w') as f :
        f.write("共花时间 %s" % time.time() - startTime)
    
    

