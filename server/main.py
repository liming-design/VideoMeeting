from enum import Enum
import time
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys
from Ui_main import Ui_MainWindow
from db import MyDataBase

import ctypes
from PyQt5 import QtWidgets,QtCore
from Processor import AudioVideoConn,InfoConn
class DataType(Enum):
    image_s_to_c=0
    image_c_to_s=3
    audio_s_to_c=1
    audio_c_to_s=4
    login_s_to_c=2
    login_c_to_s=5
    meetingid_s_to_c=6
    meetingid_c_to_s=7
    meetinfo_s_to_c=8
    meetinfo_c_to_s=9
    videorequest_s_to_c=10
    videorequest_c_to_s=11
    add_member_s_to_c=12
    del_member_s_to_c=13
    msg_s_to_c=14
    msg_c_to_s=15
    diff_image_c_to_s=16
    diff_image_s_to_c=17
    quitmeet_c_to_s=18
    memberquit_s_to_c=19
    endmeet_c_to_s=20
    endmeet_s_to_c=21
    membercamera_c_to_s=22
    membercamera_s_to_c=23
    membermicrophone_c_to_s=24
    membermicrophone_s_to_c=25
    allmute_c_to_s=26
    allmute_s_to_c=27
    unallmute_c_to_s=28
    unallmute_s_to_c=29
    register_c_to_s=30
    register_s_to_c=31
    existMeeting_c_to_s=32
    existMeeting_s_to_c=33
    changename_c_to_s=34
    changename_s_to_c=35
    changepwd_c_to_s=36
    changepwd_s_to_c=37
    handup_c_to_s=38
    handdown_c_to_s=39
    handuplist_s_to_c=40

def MySend(datatype,DataList):
    result=bytearray(1)
    result[0]=datatype.value
    for databyte in DataList:
        num=len(databyte)
        l=num.to_bytes(4,byteorder='little')
        result+=l
        result+=databyte
    return result    

def MyReceive(msg):
    result=[]
    datatype=msg[0]
    result.append(datatype)
    i=1    
    while i<len(msg):
        numtemp=msg[i:i+4]
        n = int.from_bytes(numtemp, byteorder = 'little')
        temp=msg[i+4:i+4+n]
        result.append(temp)
        i+=(n+4)
    return result

class MainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):

        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        self.mydb=MyDataBase()
        self.infoconn=None
        self.audiovideoconn=None
        self.toolButton.clicked.connect(self.StartAct)
        self.toolButton_1.clicked.connect(self.DelMeetingAct)
        self.toolButton_2.clicked.connect(self.DelAllMeetingAct)
        self.toolButton_3.clicked.connect(self.DelUserAct)
        self.toolButton_4.clicked.connect(self.DelAllUserAct)
        self.initUi()

    def closeEvent(self, event) -> None:
        if self.infoconn is not None:
            self.infoconn.stop()
        if self.audiovideoconn is not None:
            self.audiovideoconn.stop()
        event.accept()

    def DelMeetingAct(self):
        if len(self.tableWidget.selectedIndexes())!=0:
            meetingid=self.tableWidget.item(self.tableWidget.currentRow(), 0).text()
            sqlstr='delete from Meeting where MeetingId = ?'
            result=self.mydb.Execute(sqlstr,meetingid)
            self.updateMeeting()
            if result:
                Toast.toast('删除成功！')
            else:
                Toast.toast('删除失败！')

        pass

    def DelAllMeetingAct(self):
        sqlstr='delete from Meeting'
        result=self.mydb.Execute(sqlstr,[])
        self.updateMeeting()
        if result:
            Toast.toast('删除成功！')
        else:
            Toast.toast('删除失败！')
        pass

    def DelUserAct(self):
        if len(self.tableWidget_2.selectedIndexes())!=0:
            userid=self.tableWidget_2.item(self.tableWidget_2.currentRow(), 0).text()
            sqlstr='delete from User where UserId = ?'
            result=self.mydb.Execute(sqlstr,[userid,])
            self.updateUser()
            if result:
                Toast.toast('删除成功！')
            else:
                Toast.toast('删除失败！')

    def DelAllUserAct(self):
        sqlstr='delete from User'
        result=self.mydb.Execute(sqlstr,[])
        self.updateMeeting()
        if result:
            Toast.toast('删除成功！')
        else:
            Toast.toast('删除失败！')
    
    def ClearTable(self,table):
        table.setRowCount(0)
        table.clearContents()

    def updateUser(self):
        self.ClearTable(self.tableWidget_2)
        sqlstr='select * from User'
        users=self.mydb.SelectAll(sqlstr,[])
        self.AddDataToTable(users,self.tableWidget_2)
    
    def updateMeeting(self):
        self.ClearTable(self.tableWidget)
        sqlstr='select * from Meeting'
        meeting=self.mydb.SelectAll(sqlstr,[])
        self.AddDataToTable(meeting,self.tableWidget)

    def StartAct(self):
        infoportstr=self.lineEdit.text()
        avportstr=self.lineEdit_2.text()
        infoport=int(infoportstr)
        avport=int(avportstr)
        self.infoconn=InfoConn(infoport)
        self.audiovideoconn=AudioVideoConn(avport)
        ip=self.infoconn.addr[0]
        self.toolButton.setEnabled(False)
        self.lineEdit.setEnabled(False)
        self.lineEdit_2.setEnabled(False)

        msg='服务端开启成功！IP: {0}  InfoPort: {1}  AudioVideoPort: {2}'.format(ip,infoportstr,avportstr)
        self.showMsg(msg)
        l1=QLabel('IP: {0}    '.format(ip))
        l2=QLabel('InfoPort: {0}    '.format(infoportstr))
        l3=QLabel('AudioVideoPort: {0}    '.format(avportstr))
        self.statusbar.addPermanentWidget(l1)
        self.statusbar.addPermanentWidget(l2)
        self.statusbar.addPermanentWidget(l3)
        self.infoconn.QuitMeetingSignal.connect(self.OnQuitMeet)
        self.infoconn.EndMeetingSignal.connect(self.OnEndMeet)
        self.infoconn.JoinMeetingSignal.connect(self.OnJoinMeet)
        self.infoconn.MeetingSignal.connect(self.OnMeeting)
        self.infoconn.LoginSignal.connect(self.OnUserLogin)

    def initUi(self):
        self.updateMeeting()
        self.updateUser()

    def AddDataToTable(self,data,table):
        for i in range(len(data)):
            row=table.rowCount()
            column = table.columnCount()
            table.insertRow(row)
            for j in range(column) :
                item = QTableWidgetItem(str(data[i][j]))
                table.setItem(row, j, item)
            table.resizeColumnsToContents()

    def showMsg(self,msg):
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        t=[(nowtime,msg)]
        self.AddDataToTable(t,self.tableWidget_3)

    def OnUserLogin(self,datalist):
        userid=datalist[0]
        name=datalist[1]
        msg='用户{0}（{1}）登录成功！'.format(userid,name)
        self.showMsg(msg)

    def OnMeeting(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select UserName from User where UserId=?'
        name=self.mydb.SelectOne(sqlstr,[userid,])[0]
        msg='用户{0}（{1}）申请会议（{2}）'.format(userid,name,meetingid)
        self.updateMeeting()
        self.showMsg(msg)
        
    def OnJoinMeet(self,datalist):
        userid=datalist[0]
        name=datalist[1]
        meetingid=datalist[2]
        msg='用户{0}（{1}）加入会议（{2}）'.format(userid,name,meetingid)
        self.showMsg(msg)

    def OnQuitMeet(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select UserName from User where UserId=?'
        name=self.mydb.SelectOne(sqlstr,[userid,])[0]
        msg='用户{0}（{1}）退出会议（{2}）'.format(userid,name,meetingid)
        self.showMsg(msg)

    def OnEndMeet(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select UserName from User where UserId=?'
        name=self.mydb.SelectOne(sqlstr,[userid,])[0]
        msg='用户{0}（{1}）结束会议（{2}）'.format(userid,name,meetingid)
        self.showMsg(msg)

class Toast(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('toast')
        self.setWindowFlags(Qt.FramelessWindowHint)          # 去掉标题栏
        self.setStyleSheet("background-color:#3A4659;\n")
        self.gridLayout_3 = QtWidgets.QGridLayout(self)
        self.gridLayout_3.setContentsMargins(0, 0, 0, 0)   # 布局，frame布局在gridLayout_3里，gridLayout_3在窗体里，与窗体的四周的距离为（0，0，0，0）
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.currentTime= time.strftime("%H:%M %p")  # 当前时间(时：分 AM/PM)
        self.frame = QtWidgets.QFrame(self)
        # self.frame.setStyleSheet("background-color:#3A4659;\n" )
        self.frame.setObjectName("frame")

        self.gridLayout_2 = QtWidgets.QGridLayout(self.frame)
        self.gridLayout_2.setObjectName("gridLayout_2")

        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")

        self.passLabel = QtWidgets.QLabel(self.frame)
        self.passLabel.setMinimumSize(QtCore.QSize(41, 41))
        self.passLabel.setMaximumSize(QtCore.QSize(41, 41))
        # 显示图片（对/错）的文本框，由调用此py文件传入需显示的图片
        # self.passLabel.setPixmap(QtGui.QPixmap("images/pass.png"))
        self.passLabel.setObjectName("label_4")
        self.horizontalLayout.addWidget(self.passLabel)

        self.gridLayout = QtWidgets.QGridLayout()
        self.gridLayout.setObjectName("gridLayout")
        # 消息通知的文本框
        self.alertsLabel = QtWidgets.QLabel(self.frame)
        self.alertsLabel.setMinimumSize(QtCore.QSize(200, 0))       # 设置文本框最小尺寸
        self.alertsLabel.setStyleSheet("font: 20px\"微软雅黑\";color:white")
        self.alertsLabel.setText("消息通知")
        self.alertsLabel.setObjectName("label")
        self.gridLayout.addWidget(self.alertsLabel, 0, 0, 1, 1)
        # 显示时间的文本框
        self.timeLabel = QtWidgets.QLabel(self.frame)
        self.timeLabel.setStyleSheet("font: 15px\"微软雅黑\";color:white")
        self.timeLabel.setAlignment(QtCore.Qt.AlignRight|QtCore.Qt.AlignTrailing|QtCore.Qt.AlignVCenter)
        self.timeLabel.setText(self.currentTime)          # 将“currentTime”即当前时间，显示在文本框内
        self.timeLabel.setObjectName("label_3")
        self.gridLayout.addWidget(self.timeLabel, 0, 1, 1, 1)
        # 显示消息内容的文本框，由调用此py文件传入需显示的消息内容
        self.toastLabel = QtWidgets.QLabel(self.frame)
        self.toastLabel.setStyleSheet("font: 15px\"微软雅黑\";color:white")
        # self.toastLabel.setText("保存成功！")
        self.toastLabel.setObjectName("label")
        self.gridLayout.addWidget(self.toastLabel, 1, 0, 1, 1)

        self.horizontalLayout.addLayout(self.gridLayout)
        self.gridLayout_2.addLayout(self.horizontalLayout, 0, 0, 1, 1)
        self.gridLayout_3.addWidget(self.frame, 0, 0, 1, 1)
    
    @classmethod
    def toast(self,msg):
        self.ui = Toast()
        self.ui.show()
        QtCore.QTimer().singleShot(2000, self.ui.close)
        self.ui.toastLabel.setText(msg)
        # self.ui.passLabel.setPixmap(QtGui.QPixmap("images/pass.png"))
        screen = QDesktopWidget().screenGeometry()
        size = self.ui.geometry()
        self.ui.move((screen.width() - size.width()) // 2,(screen.height() - size.height()) // 2)

class CommonHelper:
    def __init__(self):
        self.styleFile='./qss/Ubuntu.qss'
        pass
 
    @staticmethod
    def readQss():
        styleFile='./qss/Ubuntu.qss'
        with open(styleFile, 'r') as f:
            return f.read()

if __name__=='__main__':
    app=QApplication(sys.argv)
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myserverid")
    window=MainWindow()
    window.setStyleSheet(CommonHelper.readQss())
    window.show()
    sys.exit(app.exec_())

    # pyinstaller -F -w  -i server.ico  main.py