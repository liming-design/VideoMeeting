# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'd:\作业记录\大四\python远程桌面视频\mine\client\Ui_ChangeInfo.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_ChangeInfo(object):
    def setupUi(self, ChangeInfo):
        ChangeInfo.setObjectName("ChangeInfo")
        ChangeInfo.resize(407, 204)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/视频会议.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        ChangeInfo.setWindowIcon(icon)
        self.gridLayout = QtWidgets.QGridLayout(ChangeInfo)
        self.gridLayout.setObjectName("gridLayout")
        self.formLayout = QtWidgets.QFormLayout()
        self.formLayout.setObjectName("formLayout")
        self.lineEdit = QtWidgets.QLineEdit(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit.setFont(font)
        self.lineEdit.setObjectName("lineEdit")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit)
        self.label = QtWidgets.QLabel(ChangeInfo)
        self.label.setMinimumSize(QtCore.QSize(115, 0))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.gridLayout.addLayout(self.formLayout, 0, 0, 1, 1)
        self.pushButton = QtWidgets.QPushButton(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.gridLayout.addWidget(self.pushButton, 0, 1, 1, 1)
        self.formLayout_2 = QtWidgets.QFormLayout()
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QtWidgets.QLabel(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_4 = QtWidgets.QLabel(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.label_2 = QtWidgets.QLabel(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.lineEdit_2 = QtWidgets.QLineEdit(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit_2.setFont(font)
        self.lineEdit_2.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.lineEdit_2)
        self.lineEdit_3 = QtWidgets.QLineEdit(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit_3.setFont(font)
        self.lineEdit_3.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.lineEdit_3)
        self.lineEdit_4 = QtWidgets.QLineEdit(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lineEdit_4.setFont(font)
        self.lineEdit_4.setEchoMode(QtWidgets.QLineEdit.Password)
        self.lineEdit_4.setObjectName("lineEdit_4")
        self.formLayout_2.setWidget(2, QtWidgets.QFormLayout.FieldRole, self.lineEdit_4)
        self.gridLayout.addLayout(self.formLayout_2, 1, 0, 1, 1)
        self.pushButton_2 = QtWidgets.QPushButton(ChangeInfo)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.pushButton_2.setFont(font)
        self.pushButton_2.setObjectName("pushButton_2")
        self.gridLayout.addWidget(self.pushButton_2, 1, 1, 1, 1)

        self.retranslateUi(ChangeInfo)
        QtCore.QMetaObject.connectSlotsByName(ChangeInfo)

    def retranslateUi(self, ChangeInfo):
        _translate = QtCore.QCoreApplication.translate
        ChangeInfo.setWindowTitle(_translate("ChangeInfo", "修改信息"))
        self.label.setText(_translate("ChangeInfo", "昵称："))
        self.pushButton.setText(_translate("ChangeInfo", "确认修改"))
        self.label_3.setText(_translate("ChangeInfo", "新密码："))
        self.label_4.setText(_translate("ChangeInfo", "确认密码："))
        self.label_2.setText(_translate("ChangeInfo", "原密码："))
        self.pushButton_2.setText(_translate("ChangeInfo", "确认修改"))
import a_rc
