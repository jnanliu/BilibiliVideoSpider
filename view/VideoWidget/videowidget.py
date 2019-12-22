# -*- coding: utf-8 -*-

import os
import sys
import random
import requests
from copy import deepcopy
from PyQt5.QtCore import * 
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
FAR_DIR = os.path.dirname(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))
sys.path.append(BASE_DIR)
sys.path.append(FAR_DIR)

from view.VideoWidget.videowidgetform import Ui_Form
from view.VideoWidget.style.ReadStyle import ReadStyle

class VideoWidget(QWidget, Ui_Form) :
    clicked = pyqtSignal(str)

    def __init__(self, aid) :
        super(VideoWidget, self).__init__()
        self.m_flag = False
        self.aid = str(aid)
        self.setupUi(self)
        self.retranslateUi(self)

    def mousePressEvent(self, event) :
        if event.buttons() == Qt.LeftButton :
            self.m_flag = True
        else :
            self.m_flag = False
        super(VideoWidget, self).mousePressEvent(event)

    def mouseReleaseEvent(self, event) :
        if self.m_flag :
            self.clicked.emit(self.aid)
        super(VideoWidget, self).mouseReleaseEvent(event)

if __name__ == '__main__' :
    app = QApplication(sys.argv)
    ui = VideoWidget()
    ui.show()
    sys.exit(app.exec_())