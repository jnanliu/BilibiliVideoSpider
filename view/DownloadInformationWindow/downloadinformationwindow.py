# -*- coding: utf-8 -*-

import os
import sys
import psutil
from copy import deepcopy
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FAR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(BASE_DIR)
sys.path.append(FAR_DIR)

from view.DownloadWidget.downloadwidget import DownloadWidget
from view.DownloadInformationWindow.downloadinformationform import Ui_MainWindow
from view.DownloadInformationWindow.style.ReadStyle import ReadStyle

class startDownloadThread(QThread) :

    start_download_signal = pyqtSignal(dict)

    def __init__(self, dict_, videoModels) :
        super(startDownloadThread, self).__init__()
        self.dict_ = dict_
        self.videoModels = videoModels

    def run(self) :
        try :
            for i in range(self.videoModels.rowCount()) :
                if self.videoModels.item(i).checkState() == Qt.Checked :
                    self.start_download_signal.emit(self.dict_[i])
        except Exception as e :
            print(e)
        self.exit()

class DownloadInformationWindow(QMainWindow, Ui_MainWindow) :

    def __init__(self, session):
        super(DownloadInformationWindow, self).__init__()
        self.itemDict = {}
        self.session = session
        self.setupUi(self)
        self.retranslateUi(self)
        self.videoModels = QStandardItemModel()
        self.listView.setModel(self.videoModels)
        self.setStyleSheet(ReadStyle.read())
        self.bind()
        self.setToolTip()

    def show(self) :
        self.filePath = "D:/Videos"
        self.fileLineEdit.setText(self.filePath)
        freeDiskSize = psutil.disk_usage(self.filePath)
        self.diskSizeLabel.setText("剩余：{}".format(self.GetSize(freeDiskSize[2])))
        super(DownloadInformationWindow, self).show()

    def close(self) :
        self.resize(316, 348)
        self.downloadListWidget.clear()
        super(DownloadInformationWindow, self).close()

    def bind(self) :
        self.closePushButton.clicked.connect(self.close)
        self.smallerPushButton.clicked.connect(self.showMinimized)
        self.filePushButton.clicked.connect(self.selectDir)
        self.downloadPushButton.clicked.connect(self.reshape)

    def setToolTip(self) :
        self.downloadPushButton.setToolTip("开始下载")
        self.filePushButton.setToolTip("选择下载路径")

    def selectDir(self) :
        self.filePath = QFileDialog.getExistingDirectory(self, "选择下载目录", self.fileLineEdit.text())
        freeDiskSize = psutil.disk_usage(self.filePath)
        self.diskSizeLabel.setText("剩余：{}".format(self.GetSize(freeDiskSize[2])))
        self.fileLineEdit.setText(self.filePath)

    def GetSize(self, size) :

        if size > 1024 ** 3 :
            return '{:.2f} GB'.format(size * 1. / 1024 ** 3)
        elif size > 1024 ** 2 :
            return '{:.2f} MB'.format(size * 1. / 1024 ** 2)
        elif size > 1024 :
            return '{:.2f} KB'.format(size * 1. / 1024)
        else :
            return '{} bytes'.format(size)

    def reshape(self) :
        if self.size() == QSize(746, 348) :
            return
        self.resize(746, 348)
        startdownloadthread = startDownloadThread(self.itemDict, self.videoModels)
        startdownloadthread.start_download_signal.connect(self.setpgbar)
        startdownloadthread.start()
        startdownloadthread.wait()

    def setpgbar(self, data) :
        if not os.path.exists(self.filePath + '/{}'.format(data['title'])) :
            os.mkdir(self.filePath + '/{}'.format(data['title']))
        pgbarWidget = DownloadWidget(url=data['videoDownloadUrl'], path=self.filePath+ '/{}'.format(data['title']) + "/{}.mp4".format(data['name']), 
            referer=data['referer'], session=self.session)
        pgbarWidget.fileNameLabel.setText(data['name'])
        pgbarWidget.setToolTip(data['name'])
        item = QListWidgetItem()
        item.setSizeHint(QSize(200, 80))
        self.downloadListWidget.addItem(item)
        self.downloadListWidget.setItemWidget(item, pgbarWidget)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.m_flag = True
            self.m_Position = event.globalPos() - self.pos()
            event.accept()
            self.setCursor(QCursor(Qt.OpenHandCursor))
            
    def mouseMoveEvent(self, QMouseEvent):
        if Qt.LeftButton and self.m_flag:  
            self.move(QMouseEvent.globalPos()-self.m_Position)
            QMouseEvent.accept()
            
    def mouseReleaseEvent(self, QMouseEvent):
        self.m_flag = False
        self.setCursor(QCursor(Qt.ArrowCursor))