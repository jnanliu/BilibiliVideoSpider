# -*- coding : utf-8 -*-

import os
import sys

if hasattr(sys, 'frozen'):
    os.environ['PATH'] = sys._MEIPASS + ";" + os.environ['PATH']

from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
sys.path.append(BASE_DIR)

from view.MainWindow.mainwindow import MainWindow
from view.DownloadInformationWindow.downloadinformationwindow import DownloadInformationWindow

class SplashPanel(QSplashScreen):
    def __init__(self):
        super(SplashPanel, self).__init__()
        self.setWindowOpacity(0.9)
        image = QPixmap("E:/Project/Python/Spider/BilibiliVideoSpider/img/loading2.gif")
        self.setPixmap(image)
        self.label = QLabel(self)
        movie = QMovie("E:/Project/Python/Spider/BilibiliVideoSpider/img/loading2.gif")
        movie.setCacheMode(QMovie.CacheAll)
        self.label.setMovie(movie)
        movie.start()
        self.show()

    def mousePressEvent(self, evt):
        pass

    def mouseDoubleClickEvent(self, *args, **kwargs):
        pass

    def enterEvent(self, *args, **kwargs):
        pass

    def mouseMoveEvent(self, *args, **kwargs):
        pass

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    splash = SplashPanel()
    ui = MainWindow()
    delayTime = 3
    timer = QElapsedTimer()
    timer.start()
    while timer.elapsed() < (delayTime * 1000) :
        app.processEvents()
    ui.AVLineEdit.setText("77105854")
    ui.uidLineEdit.setText("20351272")
    ui.show()
    splash.finish(ui)
    sys.exit(app.exec_())