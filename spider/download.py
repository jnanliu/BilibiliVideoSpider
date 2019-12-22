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
from PyQt5 import QtCore, QtGui, QtWidgets
from threading import Lock

from spider.settings import HEADERS, USERA_GENTS, DOWNLOAD_TIMEOUT

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

class DownloadSignal(QtCore.QObject) :
    
    download_proess_signal = QtCore.pyqtSignal(dict)
    
class DownloadThread(QtCore.QThread) :

    def __init__(self, url, path, referer, session) :
        super(DownloadThread, self).__init__()
        self.url = url
        self.path = path
        self.session = session
        self.session = requests.Session()
        self.headers = deepcopy(HEADERS)
        self.headers['User-Agent'] = random.choice(USERA_GENTS)
        self.headers.update(referer)
        self.signal = DownloadSignal()

    def run(self) :
        if isinstance(self.url, list) :
            self.filesize, self.fileSizeList = 0, []
            for url in self.url :
                response = self.session.get(url=url, headers = self.headers, stream=True)
                self.filesize += int(response.headers['Content-Length'])
                self.fileSizeList.append(int(response.headers['Content-Length']))
        else :
            response = self.session.get(url=self.url, headers = self.headers, stream=True)
            self.filesize = int(response.headers['Content-Length'])
        if not isinstance(self.url, list) :
            try: 
                with open(self.path, "ab") as f :
                    initialSize = os.path.getsize(self.path)
                    self.headers.update({
                        'Range': 'bytes=%d-' % initialSize
                    })
                    ret, offset,blockSize, startTime = {}, initialSize, 512, time.time()
                    response = self.session.get(url=self.url, headers = self.headers, stream=True)
                    for chunk in response.iter_content(chunk_size=blockSize) :
                        if not chunk :
                            break
                        f.seek(offset)
                        f.write(chunk)
                        f.flush()
                        downloadSize = offset + len(chunk)
                        if downloadSize > self.filesize :
                            downloadSize = self.filesize
                        speed = downloadSize / (time.time() - startTime)
                        remainTime = (self.filesize - downloadSize) / speed
                        ret["downloadSizeStr"] = "{}/{}".format(self.GetSize(downloadSize), self.GetSize(self.filesize))
                        ret["speedStr"] = "{}/S".format(self.GetSize(speed))
                        hourTime = int(remainTime / 60 ** 2)
                        minuteTime = int((remainTime - hourTime * 60 ** 2) / 60)
                        secondTime = int(remainTime - hourTime * 60 ** 2 - minuteTime * 60)
                        ret["reaminTimeStr"] = "{:02d}:{:02d}:{:02d}".format(int(hourTime), int(minuteTime), 
                            int(secondTime))
                        offset = offset + len(chunk) 
                        ret["proess"] = offset / int(self.filesize) * 100
                        self.signal.download_proess_signal.emit(ret)
            except Exception as e :
                print(e)
        else :
            try: 
                ret, offset, downloadSize, blockSize, startTime = {}, 0, 0, 512, time.time()
                for idx, url in enumerate(self.url) :
                    path = deepcopy(self.path)
                    path = path.split('.')[-2] + '-{}'.format(idx + 1) + '.flv'
                    with open(path, "ab") as f :
                        initialSize = os.path.getsize(path)
                        offset += initialSize
                        if initialSize >= self.fileSizeList[idx] :
                            downloadSize += initialSize
                            continue
                        self.headers.update({
                            'Range': 'bytes=%d-' % initialSize
                        })
                        response = self.session.get(url=url, headers=self.headers, stream=True)
                        for chunk in response.iter_content(chunk_size=blockSize) :
                            if not chunk :
                                break
                            #f.seek(offset)
                            f.write(chunk)
                            f.flush()
                            downloadSize = offset + len(chunk)
                            if downloadSize > self.filesize :
                                downloadSize = self.filesize
                            speed = downloadSize / (time.time() - startTime)
                            remainTime = (self.filesize - downloadSize) / speed
                            ret["downloadSizeStr"] = "{}/{}".format(self.GetSize(downloadSize), self.GetSize(self.filesize))
                            ret["speedStr"] = "{}/S".format(self.GetSize(speed))
                            hourTime = int(remainTime / 60 ** 2)
                            minuteTime = int((remainTime - hourTime * 60 ** 2) / 60)
                            secondTime = int(remainTime - hourTime * 60 ** 2 - minuteTime * 60)
                            ret["reaminTimeStr"] = "{:02d}:{:02d}:{:02d}".format(int(hourTime), int(minuteTime), 
                                int(secondTime))
                            offset = offset + len(chunk) 
                            ret["proess"] = offset / int(self.filesize) * 100
                            self.signal.download_proess_signal.emit(ret)
            except Exception as e :
                print(e)

        self.exit(0)
            

    def GetSize(self, size) :

        if size > 1024 ** 3 :
            return '{:.2f} GB'.format(size * 1. / 1024 ** 3)
        elif size > 1024 ** 2 :
            return '{:.2f} MB'.format(size * 1. / 1024 ** 2)
        elif size > 1024 :
            return '{:.2f} KB'.format(size * 1. / 1024)
        else :
            return '{} bytes'.format(size)