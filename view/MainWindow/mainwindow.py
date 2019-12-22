# -*- coding: utf-8 -*-

import os
import sys
import random
import requests
import queue
from copy import deepcopy
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FAR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(BASE_DIR)
sys.path.append(FAR_DIR)

from view.MainWindow.mainform import Ui_MainWindow
from view.MainWindow.style.ReadStyle import ReadStyle
from view.DownloadInformationWindow.downloadinformationwindow import DownloadInformationWindow
from view.VideoWidget.videowidget import VideoWidget
from spider.settings import HEADERS, USERA_GENTS
from spider.spider import Spider

class AvSpider(QThread) :

    spiderDone = pyqtSignal(dict)

    def __init__(self, av):
        super(AvSpider, self).__init__()
        self.spider = Spider('av', av, 0)
    
    def run(self) :
        for item in self.spider.parse() :
            self.spiderDone.emit(item)
        self.exit(0)

class UpSpider(QThread) :
    spiderDone = pyqtSignal(dict)

    def __init__(self, uid):
        super(UpSpider, self).__init__()
        self.spider = Spider('up', uid, 0)

    def run(self) :
        for item in self.spider.parse() :
            self.spiderDone.emit(item)
        self.exit(0)

class SetUpFace(QThread) :
    upFaceImage = pyqtSignal(tuple)

    def __init__(self, url, session) :
        super(SetUpFace, self).__init__()
        self.url = url
        self.session = session
    
    def run(self) :
        try :
            image = self.session.get(url=self.url).content
            self.upFaceImage.emit((image, ))
        except Exception as e :
            print(e)
        self.exit(0)

class GetVideoSize(QThread) :
    videoSize = pyqtSignal(int)

    def __init__(self, urls, headers, session):
        super(GetVideoSize, self).__init__()
        self.urls = urls
        self.headers = headers
        self.session = session
    
    def run(self) :
        try :
            for url in self.urls :
                size = int(self.session.get(url=url, headers=self.headers, stream=True, verify=False).headers['Content-Length'])
                self.videoSize.emit(size)
        except Exception as e :
            print(e)
        self.exit(0)

PicQueue = queue.Queue(500)

class SetPic(QThread) :
    picImage = pyqtSignal(tuple)

    def __init__(self, session) :
        super(SetPic, self).__init__()
        self.session = session

    def run(self) :
        while True :
            if not PicQueue.empty() :
                item = PicQueue.get()
                self.url = item['url']
                self.index = item['index']
                try :
                    image = self.session.get(url=self.url).content
                    self.picImage.emit((self.index, image))
                except Exception as e :
                    print(e)
                if item['done'] == True :
                    break
        self.exit(0)

class SavePic(QThread) :
    saveDone = pyqtSignal()

    def __init__(self, url, path, session) :
        super(SavePic, self).__init__()
        self.url = url
        self.path = path
        self.session = session

    def run(self) :
        with open(self.path, 'wb') as f :
            image = self.session.get(url=self.url).content
            f.write(image)
        self.saveDone.emit()
        self.exit(0)

class MainWindow(QMainWindow, Ui_MainWindow) :

    def __init__(self):
        super(MainWindow, self).__init__()
        self.session = requests.Session()
        self.diWindow = DownloadInformationWindow(self.session)
        self.upFace = QImage()
        self.setPicThread = SetPic(self.session)
        self.setPicThread.picImage.connect(self.setPic)
        self.videoSize = 0
        self.setupUi(self)
        self.retranslateUi(self)
        self.setStyleSheet(ReadStyle.read())
        self.bind()
        self.videos = QStandardItemModel()
        self.listView.setModel(self.videos)

    def bind(self) :
        self.closePushButton.clicked.connect(self.close)
        self.smallerPushButton.clicked.connect(self.showMinimized)
        self.AVPpushButton.clicked.connect(self.showPage)
        self.UPPushButton.clicked.connect(self.showPage)
        self.AboutPushButton.clicked.connect(self.showAbout)
        self.searchPushButton.clicked.connect(self.avSearch)
        self.searchPushButton_2.clicked.connect(self.upSearch)
        self.savePicPushButton.clicked.connect(self.savePic)
        self.AVLineEdit.returnPressed.connect(self.searchPushButton.click)
        self.uidLineEdit.returnPressed.connect(self.searchPushButton_2.click)
        self.downloadPushButton.clicked.connect(self.showDownloadInformation)

    def avSearch(self) :
        av = self.AVLineEdit.text()
        if not av.isdigit() or av == "" :
            mess = QMessageBox.warning(self, "错误", "av号格式错误", buttons=QMessageBox.Ok)
            self.AVLineEdit.setText("")
            self.AVLineEdit.setFocus()
        else :
            self.videoSize = 0
            self.videos.clear()
            self.diWindow.videoModels.clear()
            self.diWindow.itemDict.clear()
            self.avSpider = AvSpider(av)
            self.avSpider.spiderDone.connect(self.setAvInformation)
            self.avSpider.start()

    def upSearch(self) :
        uid = self.uidLineEdit.text()
        if not uid.isdigit() or uid == "" :
            mess = QMessageBox.warning(self, "错误", "uid格式错误", buttons=QMessageBox.Ok)
            self.uidLineEdit.setText("")
            self.uidLineEdit.setFocus()
        else :
            self.listWidget.clear()
            self.setPicThread.terminate()
            self.upSpider = UpSpider(uid)
            self.upSpider.spiderDone.connect(self.setUpInformation)
            self.upSpider.start()
    
    def setAvInformation(self, item) :
        self.titleLineEdit.setText(item['title'])
        self.titleLineEdit.setCursorPosition(0)
        self.authorLineEdit.setText(item['author'])
        self.descriptionTextEdit.setPlainText(item['description'])
        self.coverLineEdit.setText(item['coverImage'])
        self.coverLineEdit.setCursorPosition(0)
        self.videoItem = QStandardItem()
        self.videoItem.setCheckable(True)
        self.videoItem.setCheckState(Qt.Checked)
        self.videoItem.setText(item['name'])
        self.videos.setItem(item['page'] - 1, self.videoItem)
        self.videoItem = QStandardItem()
        self.videoItem.setCheckable(True)
        self.videoItem.setCheckState(Qt.Checked)
        self.videoItem.setText(item['name'])
        self.videoItem.setToolTip(item['name'])
        self.diWindow.videoModels.setItem(item['page'] - 1, self.videoItem)
        self.diWindow.itemDict[item['page'] - 1] = deepcopy(item)
        self.diWindow.fileNumlabel.setText(str(item['page']))
        self.headers = deepcopy(HEADERS)
        self.headers['User-Agent'] = random.choice(USERA_GENTS)
        self.headers.update(item['referer'])
        if isinstance(item['videoDownloadUrl'], list) :
            self.videoSize = 0
            self.setvideosize = GetVideoSize(item['videoDownloadUrl'], self.headers, self.session)
            self.setvideosize.videoSize.connect(self.setVideoSize)
            self.setvideosize.start()
        else :
            self.response = self.session.get(url=item['videoDownloadUrl'], headers=self.headers, stream=True, verify=False)
            self.videoSize += int(self.response.headers['Content-Length'])
        self.diWindow.fileSizeLabel.setText(self.GetSize(self.videoSize))

    def setUpInformation(self, item) :
        if item == None :
            mess = QMessageBox.warning("警告", "该up主还没有发布过视频", buttons=QMessageBox.Ok)
            return
        if item['index'] == 0 :
            self.UPNameLineEdit.setText(item['upName'])
            self.UPNameLineEdit.setCursorPosition(0)
            self.upSignTextEdit.setText(item['upSign'])
            loadingMovie = QMovie("E:/Project/Python/Spider/BilibiliVideoSpider/img/loading.gif")
            loadingMovie.setCacheMode(QMovie.CacheAll)
            loadingMovie.setScaledSize(QSize(40, 40))
            self.upFaceLabel.setMovie(loadingMovie)
            loadingMovie.start()
            self.setUpFaceThread = SetUpFace(url=item['upFace'], session=self.session)
            self.setUpFaceThread.upFaceImage.connect(self.setUpFace)
            self.setUpFaceThread.start()
            while not PicQueue.empty() :
                PicQueue.get()
            self.setPicThread.start()
        videoWidget = VideoWidget(item['aid'])
        videoItem = QListWidgetItem()
        videoItem.setSizeHint(QSize(330, 70))
        dict_ = {
            "done" : False,
            "url" : 'https:' + item['pic'],
            "index" : item['index']
        }
        if item['index'] == item['total'] :
            dict_.update({
                "done" : True
            })
        PicQueue.put(dict_)
        videoWidget.titleLabel.setText(item['title'])
        videoWidget.lengthLabel.setText(item['length'])
        videoWidget.playLabel.setText(str(item['play']))
        videoWidget.descriptionLabel.setText("")
        loadingMovie = QMovie("E:/Project/Python/Spider/BilibiliVideoSpider/img/loading.gif")
        loadingMovie.setCacheMode(QMovie.CacheAll)
        loadingMovie.setScaledSize(QSize(40, 40))
        videoWidget.picLabel.setMovie(loadingMovie)
        loadingMovie.start()
        videoWidget.setToolTip(item['description'])
        videoWidget.clicked.connect(self.jumpAvSearch)
        self.listWidget.addItem(videoItem)
        self.listWidget.setItemWidget(videoItem, videoWidget)

    def setUpFace(self, data) :
        self.upFace = QPixmap.fromImage(QImage.fromData(data[0]))
        self.upFaceLabel.setPixmap(self.upFace.scaled(40, 40))

    def setPic(self, data) :
        image = QPixmap.fromImage(QImage.fromData(data[1]))
        item = self.listWidget.item(data[0])
        widget = self.listWidget.itemWidget(item)
        widget.picLabel.clear()
        widget.picLabel.setPixmap(image.scaled(40, 40))

    def setVideoSize(self, data) :
        self.videoSize += data
        self.diWindow.fileSizeLabel.setText(self.GetSize(self.videoSize))

    def savePic(self) :
        path = QFileDialog.getExistingDirectory(self, caption="选择保存文件夹", directory="D:/")
        path = path + '/{}_封面.jpg'.format(self.titleLineEdit.text())
        self.savePicThread = SavePic(self.coverLineEdit.text(), path, self.session)
        self.savePicThread.saveDone.connect(self.showSaveMessage)
        self.savePicThread.start()

    def showSaveMessage(self) :
        mess = QMessageBox.information(self, "提示", "保存成功")

    def showPage(self) :
        dict = {
            'AVPpushButton': 0,
            'UPPushButton': 1,
        }
        index = dict[self.sender().objectName()]
        self.stackedWidget.setCurrentIndex(index)
    
    def showAbout(self) :
        mess = QMessageBox.about(self, "关于", "GitHub地址：https://github.com/Christoph-Liu")

    def showDownloadInformation(self) :
        self.diWindow.show()

    def jumpAvSearch(self, aid) :
        self.stackedWidget.setCurrentIndex(0)
        self.AVLineEdit.setText(aid)
        self.searchPushButton.click()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            
    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:  
            self.move(QMouseEvent.globalPos() - self.m_Position)
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))

    def GetSize(self, size) :

        if size > 1024 ** 3 :
            return '{:.2f} GB'.format(size * 1. / 1024 ** 3)
        elif size > 1024 ** 2 :
            return '{:.2f} MB'.format(size * 1. / 1024 ** 2)
        elif size > 1024 :
            return '{:.2f} KB'.format(size * 1. / 1024)
        else :
            return '{} bytes'.format(size)