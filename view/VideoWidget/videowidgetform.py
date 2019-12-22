# -*- coding: utf-8 -*-

from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_Form(object):
    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(330, 71)
        self.picLabel = QtWidgets.QLabel(Form)
        self.picLabel.setGeometry(QtCore.QRect(13, 10, 41, 51))
        self.picLabel.setObjectName("picLabel")
        self.titleLabel = QtWidgets.QLabel(Form)
        self.titleLabel.setGeometry(QtCore.QRect(70, 10, 251, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.titleLabel.setFont(font)
        self.titleLabel.setObjectName("titleLabel")
        self.lengthLabel = QtWidgets.QLabel(Form)
        self.lengthLabel.setGeometry(QtCore.QRect(70, 30, 121, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.lengthLabel.setFont(font)
        self.lengthLabel.setObjectName("lengthLabel")
        self.descriptionLabel = QtWidgets.QLabel(Form)
        self.descriptionLabel.setGeometry(QtCore.QRect(70, 50, 251, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.descriptionLabel.setFont(font)
        self.descriptionLabel.setObjectName("descriptionLabel")
        self.playLabel = QtWidgets.QLabel(Form)
        self.playLabel.setGeometry(QtCore.QRect(200, 30, 121, 16))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.playLabel.setFont(font)
        self.playLabel.setObjectName("playLabel")

        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.picLabel.setText(_translate("Form", "TextLabel"))
        self.titleLabel.setText(_translate("Form", "TextLabel"))
        self.lengthLabel.setText(_translate("Form", "TextLabel"))
        self.descriptionLabel.setText(_translate("Form", "TextLabel"))
        self.playLabel.setText(_translate("Form", "TextLabel"))
