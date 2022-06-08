from PyQt5 import QtWidgets
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import numpy as np
from Structure import MemberInfo
import time

class VideoLabel(QLabel):
    ImageSignal=pyqtSignal(np.ndarray)
    VolumSignal=pyqtSignal(int)
    CameraChangeSignal=pyqtSignal(str)
    MicrophoneChangeSignal=pyqtSignal(str)
    def __init__(self,info):
        super().__init__()
        self.InitUi() 
        self.info=info
        self.userid=info.userid
        self.username=info.username
        self.microphone=info.microphone
        self.camera=info.camera
        self.UpdateState()

        #region 麦克风timer
        self.MicrophoneTimer=QTimer()
        self.MicrophoneTimer.setSingleShot(True)
        self.MicrophoneTimer.timeout.connect(lambda path=':img/开启麦克风1.png':self.MicrophoneAction.setIcon(QIcon(path)))
        #endregion

        self.ImageSignal.connect(self.ShowVideo)
        self.CameraChangeSignal.connect(self.OnCameraChange)
        self.MicrophoneChangeSignal.connect(self.OnMicrophoneChange)
        self.VolumSignal.connect(self.OnVolum)

    def UpdateState(self):
        if self.camera!='11':
            self.setText(self.username)
        if self.microphone!='11':
            self.SetIcon(':img/麦克风-静音 1.png')
        else:
            self.SetIcon(':img/开启麦克风1.png')
        self.namelabel.setText(self.username)

    def InitUi(self):
        self.setAlignment(Qt.AlignCenter)
        font=QFont()
        font.setPointSize(25)
        self.setFont(font)
        # self.setFrameShape(QtWidgets.QFrame.Box)
        self.setStyleSheet('border-width: 0px;')
        
        self.frame = QtWidgets.QFrame(self)
        # self.frame.setStyleSheet('border-width: 1px;border-style: solid;')
        self.frame.setStyleSheet("background-color:rgb(170, 255, 255)")
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setFrameShadow(QtWidgets.QFrame.Plain)
        self.frame.setLineWidth(1)
        self.frame.setMinimumSize(QtCore.QSize(100, 25))
        self.frame.setMaximumSize(QtCore.QSize(121, 25))
        self.hlayout = QtWidgets.QHBoxLayout(self.frame)
        self.hlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.setSpacing(0)
        #MicrophoneAction
        self.MicrophoneAction = QtWidgets.QToolButton(self.frame)
        icon = QtGui.QIcon()
        icon=QIcon(':img/开启麦克风1.png')
        self.MicrophoneAction.setIcon(icon)
        self.MicrophoneAction.setIconSize(QtCore.QSize(25, 25))
        self.MicrophoneAction.setPopupMode(QtWidgets.QToolButton.InstantPopup)
        self.MicrophoneAction.setToolButtonStyle(QtCore.Qt.ToolButtonIconOnly)
        self.MicrophoneAction.setAutoRaise(True)
        self.hlayout.addWidget(self.MicrophoneAction)
        #namelabel
        self.namelabel = QtWidgets.QLabel(self.frame)
        self.hlayout.addWidget(self.namelabel)
        self.namelabel.setText('234')
        font = QtGui.QFont()
        font.setPointSize(10)
        self.namelabel.setFont(font)
        #region vlayout
        vlayout=QVBoxLayout()
        vlayout.addWidget(self.frame,alignment=Qt.AlignBottom)
        self.setLayout(vlayout)
        #endregion
        pass
    
    def OnCameraChange(self,camera):
        if camera!='11':
            self.setText(self.username) 
        self.camera=camera
        self.info.camera=camera

    def OnMicrophoneChange(self,microphone):
        if microphone!='11':
            self.SetIcon(':img/麦克风-静音 1.png')
        else:
            self.SetIcon(':img/开启麦克风1.png')
        self.microphone=microphone
        self.info.microphone=microphone
       
    def OnVolum(self,volum):
        basepath=':img/开启麦克风'
        label=self.MicrophoneAction
        timer=self.MicrophoneTimer
        if volum<4000:
            path=basepath+'2.png'
        elif volum<20000:
            path=basepath+'3.png'         
        elif volum>=20000:
            path=basepath+'4.png'      
        icon=QIcon(path)
        label.setIcon(icon)
        timer.start(500)  

    def ShowVideo(self,show):
        # if self.camera!='11': return
        label=self
        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)

        w_box=label.width()
        h_box=label.height()


        h = showImage.height()
        w = showImage.width()

        f1 = 1.0*w_box/w
        f2 = 1.0 * h_box / h

        factor = min([f1, f2])
        width = int(w * factor)
        height = int(h * factor)    
        showImage=showImage.scaled(width,height,Qt.KeepAspectRatio)
        label.setPixmap(QPixmap.fromImage(showImage))  
    
    def SetIcon(self,iconpath):
        icon = QtGui.QIcon()
        icon=QIcon(iconpath)
        self.MicrophoneAction.setIcon(icon)

class MainLabel(VideoLabel):
    OtherImageSignal=pyqtSignal(str,np.ndarray)
    InfoChangeSignal=pyqtSignal(MemberInfo)
    def __init__(self,info):
        super().__init__(info)
        self.frame.setMinimumSize(QtCore.QSize(151, 35))
        self.frame.setMaximumSize(QtCore.QSize(151, 35))
        self.MicrophoneAction.setIconSize(QtCore.QSize(30,30))
        self.OtherImageSignal.connect(self.OnOtherImage)
        self.InfoChangeSignal.connect(self.OnInfoChange)
        
    def OnOtherImage(self,userid,show):
        if userid==self.userid:
            self.ImageSignal.emit(show)
            
    def OnInfoChange(self,info):
        self.info=info
        self.userid=info.userid
        self.username=info.username
        self.microphone=info.microphone
        self.camera=info.camera
        self.UpdateState()
 
class MyLabel(QLabel):#支持单击的label会议id label
    clicked = pyqtSignal(QLabel)
    def __init__(self,parent=None):
        super(MyLabel, self).__init__(parent)

    def mousePressEvent(self, QMouseEvent):  # QLable的单击操作
        if QMouseEvent.button() == QtCore.Qt.LeftButton:# 判断左键按下
            self.clicked.emit(self)

class  memberWidget(QFrame):
    CameraSignal=pyqtSignal(str)
    MicrophoneSignal=pyqtSignal(str)
    VolumSignal=pyqtSignal(int)
    def __init__(self,info,parent=None):
        super().__init__(parent)
        self.userid=info.userid
        self.username=info.username
        self.microphone=info.microphone
        self.camera=info.camera
        self.InitUi()   
        #region 麦克风 Qtimer
        self.MicrophoneTimer=QTimer()
        self.MicrophoneTimer.setSingleShot(True)
        self.MicrophoneTimer.timeout.connect(lambda path=':img/开启麦克风1.png':self.MicrophoneAction.setIcon(QIcon(path)))
        #endregion
        
        self.CameraSignal.connect(self.OnCamera)
        self.MicrophoneSignal.connect(self.OnMicrophone)
        self.VolumSignal.connect(self.OnVolum)
    
    def OnVolum(self,volum):
        basepath=':img/开启麦克风'
        if volum<4000:
            path=basepath+'2.png'
        elif volum<20000:
            path=basepath+'3.png'         
        elif volum>=20000:
            path=basepath+'4.png'      
        icon=QIcon(path)
        self.MicrophoneAction.setIcon(icon)
        self.MicrophoneTimer.start(500)  
    
    def OnMicrophone(self,microphone):
        if microphone=='11':
            icon = QtGui.QIcon(":img/开启麦克风1.png")
        else:
            icon = QtGui.QIcon("img/麦克风-静音 1.png")
        self.MicrophoneAction.setIcon(icon)
        self.microphone=microphone

    def OnCamera(self,camera):
        if camera=='11':
            icon = QtGui.QIcon(":/img/摄像头.png")
        else:
            icon = QtGui.QIcon("img/摄像头_关闭.png")
        self.CameraAction.setIcon(icon)
        self.camera=camera

    def InitUi(self): 
        # self.setFrameShape(QtWidgets.QFrame.WinPanel)
        # self.setFrameShadow(QtWidgets.QFrame.Plain)
        # self.setLineWidth(1)
        # self.setStyleSheet("background-color: rgb(240,240,240);")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self)
        self.setStyleSheet('background-color:rgb(248,249,251)') 
        self.label = QtWidgets.QLabel(self)
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setFamily("Arial")
        self.label.setFont(font)
        self.horizontalLayout.addWidget(self.label)
        self.MicrophoneAction = QtWidgets.QToolButton(self)
        if self.microphone=='11':
            icon = QtGui.QIcon(":/img/开启麦克风1.png")
        else:
            icon = QtGui.QIcon("img/麦克风-静音 1.png")

        self.MicrophoneAction.setIcon(icon)
        self.MicrophoneAction.setIconSize(QtCore.QSize(25, 25))
        self.horizontalLayout.addWidget(self.MicrophoneAction)
        self.CameraAction = QtWidgets.QToolButton(self)
        if self.camera=='11':
            icon1 = QtGui.QIcon(":/img/摄像头.png")
        else:
            icon1 = QtGui.QIcon(":/img/摄像头_关闭.png")
        self.CameraAction.setIcon(icon1)
        self.CameraAction.setIconSize(QtCore.QSize(25, 25))
        self.horizontalLayout.addWidget(self.CameraAction)
        self.label.setText(self.username)

# region 气泡窗
class Ui_Dialog(object):
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(350, 54)
        Dialog.setStyleSheet("background: transparent;")
        self.pushButton = QtWidgets.QPushButton(Dialog)
        self.pushButton.setGeometry(QtCore.QRect(0, 0, 351, 51))
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.pushButton.sizePolicy().hasHeightForWidth())
        self.pushButton.setSizePolicy(sizePolicy)
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei UI")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.pushButton.setFont(font)
        self.pushButton.setFocusPolicy(QtCore.Qt.NoFocus)
        self.pushButton.setContextMenuPolicy(QtCore.Qt.NoContextMenu)
        self.pushButton.setAutoFillBackground(False)
        # 在这里设置气泡的stylesheet
        self.pushButton.setStyleSheet("background-color:rgb(250, 255, 213);\n"
"border-style:none;\n"
"padding:8px;\n"
"border-radius:25px;")
        self.pushButton.setObjectName("pushButton")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.pushButton.setText(_translate("Dialog", "提示框"))

def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate

class Toast(QDialog):
    def __init__(self, text:str, parent=None):
    	# 设置ui
        super().__init__(parent)
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)
        # 设置定时器，用于动态调节窗口透明度
        self.timer = QTimer()
        # 设置气泡在屏幕上的位置，水平居中，垂直屏幕80%位置
        desktop = QApplication.desktop()
        self.setGeometry(QRect(int(desktop.width() / 2 - 75), int(desktop.height() * 0.1), 352, 50))
        # 显示的文本
        self.ui.pushButton.setText(text)
        # 设置隐藏标题栏、无边框、隐藏任务栏图标、始终置顶
        self.setWindowFlags(Qt.CustomizeWindowHint | Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        # 设置窗口透明背景
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        # 窗口关闭自动退出，一定要加，否则无法退出
        self.setAttribute(Qt.WA_QuitOnClose, True)
        # 用来计数的参数
        self.windosAlpha = 0
        # 设置定时器25ms，1600ms记64个数
        self.timer.timeout.connect(self.hide_windows)
        self.timer.start(25)
        
	# 槽函数
    def hide_windows(self):
        self.timer.start(25)
        # 前750ms设置透明度不变，后850ms透明度线性变化
        if self.windosAlpha <= 30:
            self.setWindowOpacity(1.0)
        else:
            self.setWindowOpacity(1.882 - 0.0294 * self.windosAlpha)
        self.windosAlpha += 1
        # 差不多3秒自动退出
        if self.windosAlpha >= 63:
            self.close()
	
	# 静态方法创建气泡提示
    @staticmethod
    @static_vars(tip=None)
    def toast(text):
        Toast.toast.tip = Toast(text)
        Toast.toast.tip.show()
    
    # @classmethod
    # def show_tip(self,text):
    #     self.ui=TipUi(text)
    #     self.ui.show()
 
#endregion