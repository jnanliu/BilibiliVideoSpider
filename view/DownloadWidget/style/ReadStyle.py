# -*- coding: utf-8 -*-

import os

#BASE_DIR = os.path.abspath(os.path.dirname(__file__))

BASE_DIR = 'E:/Project/Python/Spider/BilibiliVideoSpider/view/DownloadWidget/style'

class ReadStyle() :

    @staticmethod
    def read() :
        with open(os.path.join(BASE_DIR, 'style.qss'), 'r') as f :
            return f.read()