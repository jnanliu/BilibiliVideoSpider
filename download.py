# -*- coding: utf-8 -*-
import os
import sys
import time
import requests
import queue
import random
import eprogress
from copy import deepcopy
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, wait
from requests.adapters import HTTPAdapter
from threading import Lock

from settings import HEADERS, USERA_GENTS, DOWNLOAD_TIMEOUT

lock = Lock()

class Downloaer() :

    def __init__(self, url, path, num, referer, session):
        self.url = url
        self.path = path
        self.num = num
        self.headers = deepcopy(HEADERS)
        self.headers['User-Agent'] = random.choice(USERA_GENTS)
        self.headers.update(referer)
        self.session = requests.Session()
        self.session.mount('http://', HTTPAdapter(max_retries=3))
        response = self.session.get(self.url, headers=self.headers, stream=True, verify=False)
        self.status = response.status_code
        if self.status != 200 :
            print(self.headers)
        self.size = int(response.headers['Content-Length'])
        dirname = os.path.dirname(self.path)
        if not os.path.exists(dirname) :
            os.makedirs(dirname)

    def GetSize(self, size) :

        if size > 1024 ** 3 :
            return '{:.2f} GB'.format(size * 1. / 1024 ** 3)
        elif size > 1024 ** 2 :
            return '{:.2f} MB'.format(size * 1. / 1024 ** 2)
        elif size > 1024 :
            return '{:.2f} KB'.format(size * 1. / 1024)
        else :
            return '{} bytes'.format(size)

    def PartDown(self, start, end):

        self.headers.update({"Range":"bytes=%s-%s"%(start, end)})
        downloadContent = self.session.get(self.url, headers=self.headers, stream=True, verify=False)
        with open(self.path, 'rb+') as fp :
            fp.seek(start)
            for chunk in downloadContent.iter_content(chunk_size=1024) :
                if chunk :
                    fp.write(chunk)

    def __call__(self, logger):

        fp = open(self.path, "wb")
        fp.truncate(self.size)
        fp.close()
        logger.info("%s 开始下载，文件大小为 %s %s" % (os.path.split(self.path)[-1], self.GetSize(self.size), self.status))
        part = self.size // self.num
        pool = ThreadPoolExecutor(max_workers=self.num)
        futures = []
        end = -1
        for i in range(self.num):
            start = end + 1
            end = start + part - 1
            if i == self.num - 1 :
                end = self.size - 1
            futures.append(pool.submit(self.PartDown, start, end))
        wait(futures)
        logger.info("%s 下载完成" % os.path.split(self.path)[-1])
    
