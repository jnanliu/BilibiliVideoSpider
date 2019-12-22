# -*- coding: utf-8 -*-

import os
import sys
import qtawesome as qta
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FAR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(BASE_DIR)
sys.path.append(FAR_DIR)

from view.DownloadWidget.downloadwidgetform import Ui_Form
from view.DownloadWidget.style.ReadStyle import ReadStyle
from spider.download import DownloadThread

class DownloadWidget(QWidget, Ui_Form) :
    def __init__(self, url, path, referer, session) :
        super(DownloadWidget, self).__init__()
        self.count = 0
        self.stopFlag = False
        self.url = url
        self.path = path
        self.referer = referer
        self.session = session
        self.setupUi(self)
        self.retranslateUi(self)
        self.setStyleSheet(ReadStyle.read())
        self.bind()
        self.downloader = DownloadThread(self.url, self.path, self.referer, self.session)
        self.downloader.signal.download_proess_signal.connect(self.updateProgressBar)
        self.downloader.start()

    def bind(self) :
        self.pushButton.clicked.connect(self.stop)
        self.openDirPushButton.clicked.connect(self.openDir)

    def stop(self) :
        if not self.stopFlag :
            self.pushButton.setIcon(qta.icon("fa5.play-circle", color="gray"))
            self.pushButton.setToolTip("继续")
            self.downloader.terminate()
        else :
            self.pushButton.setIcon(qta.icon("fa5.stop-circle", color="gray"))
            self.pushButton.setToolTip("暂停")
            self.downloader.start()
        self.stopFlag = not self.stopFlag

    def openDir(self) :
        os.startfile(os.path.dirname(self.path))

    def updateProgressBar(self, value) :
        if self.count % 10 == 0 :
            self.downloadSizeLabel.setText(value["downloadSizeStr"])
            self.remainTimeLabel.setText(value["reaminTimeStr"])
            self.speedLabel.setText(value["speedStr"])
        self.progressBar.setValue(int(value["proess"]))
        self.count = self.count + 1