# -*- coding: utf-8 -*-
import os
import json
import subprocess
import requests

from settings import FILE_PATH

class Process() :

    def __init__(self, item) :
        
        self.path = FILE_PATH
        self.item = item

    def __getitem__(self, key) :

        return self.item[key]

    def __call__(self) :

        item = self.item
        if isinstance(item['videoDownloadUrl'], list) :
            for idx, url in enumerate(item['videoDownloadUrl']) :
                title = item['title']
                pageNumber = "分p{}---".format(item['page']) + item['name']
                name = item['name'] + '---{}.mp4'.format(idx + 1)
                videoFilePath = os.path.join(FILE_PATH, '%s\%s\%s' % (title, pageNumber, name))
                imagePath = os.path.join(FILE_PATH, '%s\%s\%s' % (title, pageNumber,'封面.jpg'))
                yield videoFilePath, url, None, None, item['coverImage'], imagePath
        else :
            title = item['title']
            pageNumber = "分p{}---".format(item['page']) + item['name']
            name = item['name']
            videoFilepath = os.path.join(FILE_PATH, '%s\%s\%s.mp4' % (title, pageNumber, name))
            audioFilepath = os.path.join(FILE_PATH, '%s\%s\%s.mp3' % (title, pageNumber, name))
            imagePath = os.path.join(FILE_PATH, '%s\%s\%s' % (title, pageNumber, '封面.jpg'))
            yield videoFilepath, item['videoDownloadUrl'], audioFilepath, \
                 item['audioDownloadUrl'], item['coverImage'], imagePath
