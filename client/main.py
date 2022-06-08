from PyQt5 import QtWidgets
from PyQt5 import QtCore,QtGui
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import sys,random
import numpy as np
import datetime
from Ui_main import Ui_Main
from Ui_meet import  Ui_MeetWindow
from Ui_login import Ui_Login
from Ui_JoinMeeting import Ui_JoinMeet
from Ui_ChangeInfo import Ui_ChangeInfo
import configparser
import ctypes
from CustomControl import VideoLabel,MainLabel,MyLabel,Toast,memberWidget
from Structure import State,MemberInfo,DataType
from Processor import DesktopProcessor, PyRecord,VideoProcessor,AudioProcessor,InfoConn,AudioVideoConn
from Tools import DES

def readConfig(key1,key2):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config[key1][key2]

class LoginWindow(QDialog,Ui_Login):
    ArgsSignal=pyqtSignal(list)
    def __init__(self, parent=None):
        super(LoginWindow, self).__init__(parent)
        self.setupUi(self)
        self.setAttribute(Qt.WA_DeleteOnClose) #考虑到安全性，加上这一句，关闭该窗口的同时，释放掉内存，保护密码等隐私数据
        self.state=State()
        self.state.infoconn=InfoConn()
        self.timer=QTimer()
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.OntimeOut)
        
        rp=self.readConfig('login_default','remember_password')
        al=self.readConfig('login_info','user_id') 
        userid=self.readConfig('login_info','user_id')
        self.lineEdit1.setText(userid)

        self.pushButton.clicked.connect(self.LoginAct)
        self.pushButton_2.clicked.connect(self.RegisterAct)
        self.state.infoconn.LoginSignal.connect(self.OnLogin)
        self.state.infoconn.RegisterSignal.connect(self.OnRegister)
        if rp=='yes':
            enpwd=self.readConfig('login_info','pwd')
            key=self.readConfig('login_info','secret_key')
            # pwd=DES.des_decrypt(enpwd,key)
            pwd=DES.AES_Decrypt(enpwd,key)
            self.lineEdit2.setText(pwd)
            self.checkBox1.setChecked(True)
        if al=='yes':
            self.checkBox2.setChecked(True)           
            self.LoginAct()
    def readConfig(self,key1,key2):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config[key1][key2]

    def writeConfig(self,data,key1,key2):
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set(key1, key2, data) 
        config.write(open("config.ini", "r+", encoding="utf-8"))

    def getRandomstr(self):
        num = random.randint(00000000,99999999)
        numstr=str(num)
        return numstr

    def LoginAct(self):
        id=self.lineEdit1.text()
        pwd=self.lineEdit2.text()

        if id!=''and pwd!='':
            self.state.userid=id
            secretKey=self.readConfig('login_info','secret_key')
            if secretKey =='':
                secretKey=self.getRandomstr()
                self.writeConfig(secretKey,'login_info','secret_key')
            # pwd=DES.des_encrypt(pwd,secretKey)
            pwd=DES.AES_Encrypt(pwd,secretKey)
            self.state.infoconn.Send(DataType.login_c_to_s,[id,pwd])

            self.timer.start(2000)

            # Toast.toast('自动登录中...')
        else:
            self.label_3.setText('用户名或密码不能为空！')

    def OntimeOut(self):
        Toast.toast('连接超时！')
        # self.timer.stop()

    def OnLogin(self,datalist):
        result=datalist[0]
        if result=='1':
            username=datalist[1]
            self.state.username=username
            enpwd=self.readConfig('login_info','pwd')
            key=self.readConfig('login_info','secret_key')
            # pwd=DES.des_decrypt(enpwd,key)
            pwd=DES.AES_Decrypt(enpwd,key)
            if self.lineEdit2.text()!=pwd:
                newpwd=self.lineEdit2.text()
                # enpwd=DES.des_encrypt(newpwd)
                enpwd=DES.AES_Encrypt(newpwd,key)
                self.writeConfig(enpwd,'login_info','pwd')

            self.ArgsSignal.emit([self.state.userid,self.state.username,self.state.infoconn])
            # self.mainwin=MainWindow(self.state)
            # self.mainwin.setStyleSheet(CommonHelper.readQss())
            # self.mainwin.show()
            self.timer.stop()
            self.accept()
            # self.close()
        else:
            Toast.toast('用户名或密码错误！')

    def OnRegister(self,datalist):
        userid=datalist[0]
        Toast.toast('注册成功！用户ID为'+userid)
        self.lineEdit1.setText(userid)
        self.lineEdit2.setText('')
        self.tabWidget.setCurrentIndex(0)

    def RegisterAct(self):
        name=self.lineEdit2_1.text()
        pwd=self.lineEdit2_2.text()
        pwd2=self.lineEdit2_3.text()
        username_element_list = ('A','B','C','D','E','F','G','H','I','J','K','L',
                                    'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                                    'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
                                    'r','s','t','u','v','w','x','y','z',
                                    '1','2','3','4','5','6','7','8','9','_')
        if pwd != pwd2:
            Toast.toast('两次密码不一致!')
            return
        if name =='' or pwd=='':
            Toast.toast('用户昵称或密码不能为空！')
            return
        for i in name :
            if i not in username_element_list:
                Toast.toast('用户名只能包括大写字母、小写字母、数字、下划线_')
                return
        secretKey=self.readConfig('login_info','secret_key')
        if secretKey =='':
                secretKey=self.getRandomstr()
                self.writeConfig(secretKey,'login_info','secret_key')
        pwd=DES.AES_Encrypt(pwd,secretKey)
        # pwd=DES.des_encrypt(pwd,secretKey)
        self.state.infoconn.Send(DataType.register_c_to_s,[name,pwd])

class MainWindow(QWidget,Ui_Main):
    def __init__(self,parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)
        # self.state=state


        self.pushButton_2.clicked.connect(self.QuickMeetAct)
        self.pushButton.clicked.connect(self.JoinMeetAct)
        self.toolButton.clicked.connect(self.ChangeInfoAct)

    def OnInit(self,args):
        self.state=State()
        self.state.userid=args[0]
        self.state.username=args[1]
        self.state.infoconn=args[2]

        microphone='11'
        camera='11'
        self.state.microphone=microphone
        self.state.camera=camera
        self.state.infoconn.MeetidSignal.connect(self.OnMyMeetingid)
        
        self.label_4.setText(self.state.userid)
        self.label.setText(self.state.username)

    def ChangeInfoAct(self):
        self.win=ChangeInfoWindow(self.state)
        self.win.setStyleSheet(CommonHelper.readQss())
        self.win.changenameSignal.connect(self.OnChangeName)
        self.win.show()

    def OnChangeName(self,datalist):
        result=datalist[0]
        if result:
            name=datalist[1]
            self.label.setText(name)



    def JoinMeetAct(self):
        # args={'username':self.state.username}
        self.joinwin=JoinWindow(self.state)
        self.joinwin.JoinMeetSignal.connect(self.OnMeetingid)
        self.joinwin.setStyleSheet(CommonHelper.readQss())
        self.joinwin.show()
        pass

    def MeetWinClose(self):
        self.show()

    def QuickMeetAct(self):
        microphone=self.state.microphone
        camera=self.state.camera
        userid=self.state.userid
        self.state.infoconn.Send(DataType.meetingid_c_to_s,[userid,microphone,camera])
    
    def OnMeetingid(self,meetingid):
        self.state.meetingid=meetingid
        self.win=MeetWindow(self.state)

        self.win.QuitSignal.connect(self.MeetWinClose)
        self.win.setStyleSheet(CommonHelper.readQss())
        self.win.show()
        self.hide()
    def OnMyMeetingid(self,meetingid):
        self.state.meetingid=meetingid
        self.state.host=self.state.userid
        self.win=MeetWindow(self.state)

        self.win.QuitSignal.connect(self.MeetWinClose)
        self.win.setStyleSheet(CommonHelper.readQss())
        self.win.show()
        self.hide()

    def closeEvent(self, event) -> None:
        self.state.infoconn.stop()

class MeetWindow(QMainWindow, Ui_MeetWindow):
    QuitSignal=pyqtSignal()
    ImageSignal=pyqtSignal(str,np.ndarray)
    MyImageSignal=pyqtSignal(np.ndarray)
    def __init__(self,state, parent=None):
        #region 初始化变量
        super(MeetWindow, self).__init__(parent)
        self.setupUi(self)
        self.state=state
        self.VideoCapacityNum=4
        self.MeetIsEnd=False
        self.py_record=None
        self.start_time=datetime.datetime.now()
        self.HandDownTimer=QTimer()
        self.HandDownTimer.timeout.connect(self.OnSendHandDown)
        self.HandDownTimer.setSingleShot(True)
        self.IsMute=False
        self.ap=None
        #endregion
        
        #region 设置显示时间
        self.timeQtimer=QTimer()
        self.timeQtimer.timeout.connect(self.showTime)
        self.timeQtimer.start(500)
        #endregion

        self.ImageSignal.connect(self.OnImageSignal)
        self.MyImageSignal.connect(self.OnMyImage)

        #region Mainlabel
        member=MemberInfo(self.state.userid,self.state.username,self.state.microphone,self.state.camera)
        self.Mainlabel=MainLabel(member)
        self.horizontalLayout.insertWidget(0,self.Mainlabel)
        #endregion

        #region dockWidget
        self.dockWidget=QDockWidget()
        self.dockWidget.setStyleSheet(CommonHelper.readQss())
        #把标题栏去掉
        titleBar=QWidget()
        self.dockWidget.setTitleBarWidget(titleBar)
        self.chatwin=ChatWin(self.state)
        self.memberwin=MemberListWin(self.state)
        self.tabWidget=QTabWidget()
        self.tabWidget.addTab(self.chatwin,' 聊天 ')
        self.tabWidget.addTab(self.memberwin,' 成员 ')
        self.tabWidget.setStyleSheet("QTabBar::tab{height:46}")
        font=self.getFont(12)
        self.tabWidget.setFont(font)
        self.dockWidget.setWidget(self.tabWidget)
        self.dockWidget.setFeatures(QtWidgets.QDockWidget.AllDockWidgetFeatures)
        self.dockWidget.setAllowedAreas(QtCore.Qt.RightDockWidgetArea)

        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.dockWidget)
        self.dockWidget.hide()
        #endregion

        self.state.infoconn.MeetInfoSignal.connect(self.OnMeetInfo)
        self.state.infoconn.AddMemberSignal.connect(self.OnAddMember)
        self.state.infoconn.MsgSignal.connect(self.OnMsg)
        self.state.infoconn.QuitMeetSignal.connect(self.OnMemberQuit)
        self.state.infoconn.EndMeetSignal.connect(self.OnEndMeet)
        self.state.infoconn.MemberCameraSignal.connect(self.OnMemberCamera)
        self.state.infoconn.MemberMicrophoneSignal.connect(self.OnMemberMicrophone)
        self.state.infoconn.HandUpListSignal.connect(self.OnHandUpList)
        self.state.infoconn.AllMuteSignal.connect(self.OnAllMute)
        self.state.infoconn.UnAllMuteSignal.connect(self.OnUnAllMute)
        #region 会议号label
        self.meetid_label=MyLabel(self)
        self.meetid_label.setToolTip('点击复制会议号！')
        font=self.getFont(12)
        self.meetid_label.setFont(font)
        self.meetid_label.setText('会议ID：'+self.state.meetingid)
        self.horizontalLayout_4.insertWidget(0,self.meetid_label)
        
        #endregion
              
        #region 音视频连接器
        self.state.audiovideoconn=AudioVideoConn()
        # self.state.audiovideoconn.ImageSignal.connect(self.OnConnImage)#显示对方图像
        self.state.audiovideoconn.ImageSignal.connect(self.OnImageSignal)#显示对方图像

        #endregion
        
        #region发送会议信息请求
        audioport=str(self.state.audiovideoconn.selfport)
        self.state.audioport=audioport
        t=[self.state.meetingid,self.state.userid,self.state.microphone,self.state.camera,audioport]
        self.state.infoconn.Send(DataType.meetinfo_c_to_s,t)
        #endregion
        
        #region 把自己添加到成员列表
        # member=MemberInfo(self.state.userid,self.state.username,self.state.microphone,self.state.camera)
        self.widget=self.addMember(member)
        #endregion
              
        #region讲话人label QTimer
        self.talkpeopleTimer=QTimer()
        self.talkpeopleTimer.setSingleShot(True)
        self.talkpeopleTimer.timeout.connect(lambda t=' ':self.TalkingLabel.setText(t))
        #endregion
        
        #region 麦克风 Qtimer
        self.MicrophoneTimer=QTimer()
        self.MicrophoneTimer.setSingleShot(True)
        self.MicrophoneTimer.timeout.connect(lambda path=':img/开启麦克风1.png':self.MicrophoneAction.setIcon(QIcon(path)))
        #endregion
                     
        #region 视频处理器
        self.vp=VideoProcessor(self.state)
        # self.vp.ImageSignal.connect(self.Mainlabel.ImageSignal)#主label 显示自己图像 
        # self.vp.ImageSignal.connect(self.widget.ImageSignal)
        self.vp.ImageSignal.connect(self.MyImageSignal)
        self.dp=None
        
        
        #endregion

        #region音频处理器
        self.ap=AudioProcessor(self.state)
        self.ap.talkingSignal.connect(self.OnTalking)
        #endregion

        #region事件连接
        self.listWidget.verticalScrollBar().valueChanged.connect(self.listScrollvalueChanged)
        self.listWidget.verticalScrollBar().rangeChanged.connect(self.listScrollrangeChanged)
        self.meetid_label.clicked.connect(self.CopyMeetId)
        self.CheatAction.clicked.connect(self.cheatWinSwitch)
        self.MicrophoneAction.clicked.connect(self.MicrophoneSwitch)
        self.CameraAction.clicked.connect(self.CameraSwitch)
        self.MemberAction.clicked.connect(self.MemberSwitch)
        self.listWidget.itemSelectionChanged.connect(self.OnSelectionChanged)
        self.DesktopShareAction.clicked.connect(self.DesktopShareAct)
        self.RecordAction.clicked.connect(self.OnRecordAction)
        if self.state.host == self.state.userid:
            self.HandUpAction.setText('举手列表')
            self.handuplistWin=HandUpListWidget()
            
            self.HandUpAction.clicked.connect(self.OnHandListAction)
        else:
            self.HandUpAction.pressed.connect(self.OnHandUpActionPressed)
            self.HandUpAction.released.connect(self.OnHandUpActionReleased)
            # self.HandUpAction.clicked.connect(self.OnHandUpAction)
        #endregion
        
        # 最后根据会议信息调整状态
        self.adjustment_state()   #保证会议信息得到后再进行最后的调整
    
    def adjustment_state(self):
        if self.IsMute:
            if self.MicrophoneAction.text()=='静音':#设为静音
                if self.MicrophoneTimer.isActive():
                    self.MicrophoneTimer.stop()
                icon=QIcon(':img/麦克风-静音 1.png')
                self.MicrophoneAction.setText('开启')
                self.MicrophoneAction.setIcon(icon)      
                t='00'      
                self.state.microphone=t
                self.widget.MicrophoneChangeSignal.emit(t)       #videolabellist中的自己
                if self.state.userid==self.Mainlabel.userid:
                    self.Mainlabel.MicrophoneChangeSignal.emit(t) #主label中的自己
                self.memberwin.MicrophoneChangeSignal.emit(self.state.userid,t)  #成员列表中的自己         
                self.ap.pause()
                Toast.toast('主持人将你设为静音！')


    def OnAllMute(self):
        # 将所有人麦克风权限改为00
        #修改memberlist
        hostid=self.state.host
        for i in range(0,len(self.state.memberlist)):
            userid=self.state.memberlist[i][0]
            if hostid != userid:
                self.state.memberlist[i][2]='00'

        # 向所有窗体发送静音信号
        # 修改自己
        if self.MicrophoneAction.text()=='静音':#设为静音
            if self.MicrophoneTimer.isActive():
                self.MicrophoneTimer.stop()
            icon=QIcon(':img/麦克风-静音 1.png')
            self.MicrophoneAction.setText('开启')
            self.MicrophoneAction.setIcon(icon)      
            t='00'      
            self.state.microphone=t
            # self.widget.MicrophoneChangeSignal.emit(t)       #videolabellist中的自己
            # if self.state.userid==self.Mainlabel.userid:
            #     self.Mainlabel.MicrophoneChangeSignal.emit(t) #主label中的自己
            # self.memberwin.MicrophoneChangeSignal.emit(self.state.userid,t)  #成员列表中的自己         
            self.ap.pause()
        else:
            pass
        # 修改其他人
        microphone='00'
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if hostid != widget.userid:
                widget.MicrophoneChangeSignal.emit(microphone) #videolabel 中的

        if hostid != self.Mainlabel.userid:
            self.Mainlabel.MicrophoneChangeSignal.emit(microphone)

        self.memberwin.AllMuteSignal.emit() #成员列表中的
        
        # 弹出提示信号
        Toast.toast('管理员已经设为全员静音！')

    def OnUnAllMute(self):
        hostid=self.state.host
        # 将所有人麦克风权限改为10
        #修改memberlist
        for i in range(0,len(self.state.memberlist)):
            userid=self.state.memberlist[i][0]
            if hostid != userid:
                self.state.memberlist[i][2]='10'

        # 向所有窗体发送解除静音信号
        # 修改自己
        self.state.microphone='10'

        # 修改除了主持人外的其他人
        microphone='10'
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if hostid != widget.userid:               # 修改除了主持人外的其他人
                widget.MicrophoneChangeSignal.emit(microphone) #videolabel 中的

        if hostid != self.Mainlabel.userid:
            self.Mainlabel.MicrophoneChangeSignal.emit(microphone)

        self.memberwin.UnAllMuteSignal.emit() #成员列表中的
        # 弹出提示信号
        Toast.toast('管理员已经解除全员静音！')
        

    def OnSendHandDown(self):                 #放手timer计时器触发事件
        meetingid=self.state.meetingid
        userid=self.state.userid
        self.state.infoconn.Send(DataType.handdown_c_to_s,[userid,meetingid])
    
    def OnHandUpActionPressed(self):
        #发射举手信号
        if self.HandDownTimer.isActive:
            self.HandDownTimer.stop()
        meetingid=self.state.meetingid
        userid=self.state.userid
        self.state.infoconn.Send(DataType.handup_c_to_s,[userid,meetingid])
        Toast.toast('长按举手！')

    def OnHandUpActionReleased(self):
        self.HandDownTimer.start(3000)
        Toast.toast('松开后3秒后放下举手！')

    def OnHandListAction(self):
        if self.handuplistWin.isVisible()==True:
            self.handuplistWin.close()
        else:
            self.handuplistWin.show()
    
    def OnHandUpList(self,datalist):

        self.handuplistWin.dataSignal.emit(datalist)

    def showTime(self):
        t=str(datetime.datetime.now()-self.start_time)[:7]
        self.time_label.setText('时间：'+t)

    def OnRecordAction(self):
        if self.RecordAction.text()=='录制':
            icon=QIcon(":img/结束录制.png")
            self.RecordAction.setIcon(icon)
            self.RecordAction.setText('结束录制')
            if self.py_record is None:
                self.py_record=PyRecord()
                self.py_record.MsgSignal.connect(self.OnRecordMsg)
            self.py_record.run()
        else:
            icon=QIcon(':img/录制.png')
            self.RecordAction.setIcon(icon)
            self.RecordAction.setText('录制')
            self.py_record.stop()

    def OnRecordMsg(self,msg):
        if msg=='开始录制！':
            self.state_label.setText('正在录制！')
            png = QPixmap(':img/录制中.png')
            self.image_label.setPixmap(png)
            self.image_label.setScaledContents(True)
        elif msg=='正在停止录制！':
            self.image_label.setPixmap(QPixmap(""))
            Toast.toast(msg)
        elif msg=='正在删除缓存文件！':
            self.state_label.setText(msg)
        elif msg=='删除缓存文件成功！':
            self.state_label.setText(' ')
            Toast.toast(msg)
            self.py_record=None

        elif msg=='合并视频&音频文件成功！':
            Toast.toast(msg)
        elif msg=='正在合并视频&音频文件···':
            self.state_label.setText(msg)
        
    def OnMyImage(self,show):
        self.widget.ImageSignal.emit(show)
        if self.Mainlabel.userid==self.state.userid:
            self.Mainlabel.ImageSignal.emit(show)

    def OnImageSignal(self,userid,show):
        widget=self.getWidgetByUserId(userid)
        widget.ImageSignal.emit(show)
        if self.Mainlabel.userid==userid:
            self.Mainlabel.ImageSignal.emit(show)
      
    def DesktopShareAct(self):
        if self.DesktopShareAction.text()=='桌面共享':
            self.DesktopShareAction.setText('关闭共享')
            # self.vp.pause()
            if self.CameraAction.text()=='关闭':
                self.CameraSwitch()
            self.CameraAction.setEnabled(False)
            if self.dp==None:
                self.dp=DesktopProcessor(self.state)
                self.dp.ImageSignal.connect(self.OnMyImage)
            else:
                self.dp.resume()
        else:
            self.DesktopShareAction.setText('桌面共享')
            self.dp.pause()
            self.CameraSwitch()
            self.CameraAction.setEnabled(True)

    def OnMemberCamera(self,datalist):
        userid=datalist[0]
        camera=datalist[1]
        widget=self.getWidgetByUserId(userid)
        widget.CameraChangeSignal.emit(camera)
        if userid==self.Mainlabel.userid:
            self.Mainlabel.CameraChangeSignal.emit(camera)
        self.memberwin.CameraChangeSignal.emit(userid,camera)
        #修改memberlist
        for i in range(0,len(self.state.memberlist)):
            if self.state.memberlist[i][0]==userid:
                self.state.memberlist[i][3]=camera
                break
    
    def OnMemberMicrophone(self,datalist):
        userid=datalist[0]
        microphone=datalist[1]
        widget=self.getWidgetByUserId(userid)
        widget.MicrophoneChangeSignal.emit(microphone) #videolabel 中的
        if userid==self.Mainlabel.userid:
            self.Mainlabel.MicrophoneChangeSignal.emit(microphone)
        self.memberwin.MicrophoneChangeSignal.emit(userid,microphone) #成员列表中的
        #修改memberlist
        for i in range(0,len(self.state.memberlist)):
            if self.state.memberlist[i][0]==userid:
                self.state.memberlist[i][2]=microphone
                break

    def OnEndMeet(self):
        self.MeetIsEnd=True
        dialog=EndMeetWin(self)
        if dialog.exec_():
            self.vp.stop()
            self.ap.stop()
            self.state.audiovideoconn.stop()
            if self.dp!=None:
                self.dp.stop()
            if self.py_record != None:
                self.py_record.stop()
        self.QuitSignal.emit()
        self.close()
 
    def OnMemberQuit(self,userid):
        self.memberwin.MemberQuitSignal.emit(userid)
        #region删除用户列表
        l=len(self.state.memberlist)
        for i in range(l):
            if self.state.memberlist[i][0]==userid:
                self.state.memberlist.pop(i)
        #endregion
        
        #region 删除listwidget中
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if widget.userid==userid:
                self.listWidget.takeItem(i)
                self.listWidget.removeItemWidget(item)
                break
        #endregion
        self.UpdateNum()

    def OnMsg(self,datalist):
        username=datalist[0]
        msg=datalist[1]
        self.chatwin.MsgSignal.emit(username,msg)
        if self.dockWidget.isHidden():
            icon=QIcon(':img/消息红点.png')
            self.CheatAction.setIcon(icon)
            pass

    def cheatWinSwitch(self):  
        if self.dockWidget.isHidden():      
            w=self.width()
            h=self.height()
            desktop = QApplication.desktop()
            max=desktop.width()
            self.dockWidget.show()   
            dw=self.dockWidget.width()
            if w+dw<max:
                self.resize(w+dw,h)   
            icon=QIcon(':img/消息.png')
            self.CheatAction.setIcon(icon)       
            self.tabWidget.setCurrentWidget(self.chatwin)
        elif self.tabWidget.currentWidget()==self.chatwin:
            self.dockWidget.hide()
            w=self.width()
            h=self.height()
            dw=self.dockWidget.width()
            self.resize(w-dw,h)
        else:
            self.tabWidget.setCurrentWidget(self.chatwin)  

    def MemberSwitch(self):
        if self.dockWidget.isHidden():      
            w=self.width()
            h=self.height()
            self.dockWidget.show()   
            desktop = QApplication.desktop()
            max=desktop.width()
            dw=self.dockWidget.width()
            if w+dw<max:
                self.resize(w+dw,h)
            self.tabWidget.setCurrentWidget(self.memberwin) 
        elif self.tabWidget.currentWidget()==self.memberwin:
            self.dockWidget.hide()
            w=self.width()
            h=self.height()
            dw=self.dockWidget.width()
            self.resize(w-dw,h)
        else:
            self.tabWidget.setCurrentWidget(self.memberwin) 

    def OnSelectionChanged(self):
        currentImgIdx = self.listWidget.currentIndex().row()
        item=self.listWidget.item(currentImgIdx)
        widget=self.listWidget.itemWidget(item)
        if self.Mainlabel.userid != widget.userid:
            self.Mainlabel.InfoChangeSignal.emit(widget.info)
           
    def CameraSwitch(self):
        if self.CameraAction.text()=='关闭':#关闭
            icon=QIcon(':img/摄像头_关闭.png')
            self.CameraAction.setText('视频')
            self.CameraAction.setIcon(icon)
            t=self.state.camera[0]+'0'
            self.state.camera=t
            self.widget.CameraChangeSignal.emit(t)
            if self.state.userid==self.Mainlabel.userid:
                self.Mainlabel.CameraChangeSignal.emit(t)
            self.memberwin.CameraChangeSignal.emit(self.state.userid,t)
            self.state.infoconn.Send(DataType.membercamera_c_to_s,[self.state.userid,self.state.meetingid,t])          
            self.vp.pause()
        else:#打开
            if self.state.camera[0]=='1':
                icon=QIcon(':img/摄像头.png')
                self.CameraAction.setText('关闭')
                self.CameraAction.setIcon(icon)
                t=self.state.camera[0]+'1'
                self.state.camera=t          
                self.widget.CameraChangeSignal.emit(t)
                if self.state.userid==self.Mainlabel.userid:
                    self.Mainlabel.CameraChangeSignal.emit(t)
                self.memberwin.CameraChangeSignal.emit(self.state.userid,t)
                
                self.state.infoconn.Send(DataType.membercamera_c_to_s,[self.state.userid,self.state.meetingid,t])          
                self.vp.resume()
            else:
                Toast.toast('管理员将你设为禁止摄像头！') 

    def MicrophoneSwitch(self):     
        if self.MicrophoneAction.text()=='静音':#设为静音
            if self.MicrophoneTimer.isActive():
                self.MicrophoneTimer.stop()
            icon=QIcon(':img/麦克风-静音 1.png')
            self.MicrophoneAction.setText('开启')
            self.MicrophoneAction.setIcon(icon)
            t=self.state.microphone[0]+'0'
            self.state.microphone=t
            self.widget.MicrophoneChangeSignal.emit(t)
            if self.state.userid==self.Mainlabel.userid:
                self.Mainlabel.MicrophoneChangeSignal.emit(t)
            self.memberwin.MicrophoneChangeSignal.emit(self.state.userid,t)
            
            self.state.infoconn.Send(DataType.membermicrophone_c_to_s,[self.state.userid,self.state.meetingid,t])
            self.ap.pause()
        else:
            if self.state.microphone[0]=='1':#设为开启
                icon=QIcon(':img/开启麦克风1.png')
                self.MicrophoneAction.setText('静音')
                self.MicrophoneAction.setIcon(icon)
                t='11'
                self.state.microphone=t
                self.widget.MicrophoneChangeSignal.emit(t)
                if self.state.userid==self.Mainlabel.userid:
                    self.Mainlabel.MicrophoneChangeSignal.emit(t)
                self.memberwin.MicrophoneChangeSignal.emit(self.state.userid,t)
                
                self.state.infoconn.Send(DataType.membermicrophone_c_to_s,[self.state.userid,self.state.meetingid,t])
                self.ap.resume()

            else:
                Toast.toast('管理员将你设为静音！')
           
    def OnTalking(self,userid,volum):
        if userid==self.state.userid :
            if  self.state.microphone=='11': 
                name=self.state.username
                self.OnVolum(volum,self.MicrophoneAction,self.MicrophoneTimer)#主按钮闪动
                self.widget.VolumSignal.emit(volum)#列表按钮闪动
                if userid==self.Mainlabel.userid:
                    self.Mainlabel.VolumSignal.emit(volum)
            else:
                return
           
        else:
            widget=self.getWidgetByUserId(userid)
            if widget.microphone=='11':
                name=widget.username
                widget.VolumSignal.emit(volum)#列表按钮闪动
                if userid==self.Mainlabel.userid:
                    self.Mainlabel.VolumSignal.emit(volum)
            else:
                return
        self.TalkingLabel.setText(name)
        self.talkpeopleTimer.start(1000)
        if not self.dockWidget.isHidden() and self.tabWidget.currentWidget()==self.memberwin:
            self.memberwin.VolumSignal.emit(userid,volum)  
        pass
    
    def OnVolum(self,volum,label,timer):
        basepath=':img/开启麦克风'
        if volum<4000:
            path=basepath+'2.png'
        elif volum<20000:
            path=basepath+'3.png'         
        elif volum>=20000:
            path=basepath+'4.png'      
        icon=QIcon(path)
        label.setIcon(icon)
        timer.start(500)  

    def getNameById(self,userid):
        for member in self.state.memberlist:
            if member[0]==userid:
                return member[1]
        return None
        pass

    def OnAddMember(self,userinfo):
        member=MemberInfo(*userinfo)
        widget=self.addMember(member)
        self.state.memberlist.append(userinfo)

        num=len(self.state.memberlist)
        self.UpdateNum(num+1)

        self.memberwin.AddMemberSignal.emit(userinfo)

        if num+1 < self.VideoCapacityNum:
        #假装滚动条滚动，发射
            scrollvalue=self.listWidget.verticalScrollBar().value()
            self.listScrollvalueChanged(scrollvalue)

    def UpdateNum(self,num=None):
        if num is None:
            num=len(self.state.memberlist)+1
        self.num_label.setText(str(num)+'人在会议中')
        pass

    def getFont(self,size,fontFamily='Arial'):
        font = QtGui.QFont()
        font.setFamily(fontFamily)
        font.setPointSize(size)
        # font.setBold(False)
        return font

    def CopyMeetId(self,label):
        clipboard = QApplication.clipboard()
        clipboard.setText(self.state.meetingid)
        pass
  
    def resizeEvent(self,event):#窗体大小改变事件
        listheight=self.listWidget.height()
        num0=listheight/200
        num=listheight//200
        if num0>num: num+=1

        self.VideoCapacityNum=num
    
    def listScrollvalueChanged(self,value):#滚动条滑动事件
        first=value
        if first+self.VideoCapacityNum < self.listWidget.count()-1:
            end=first+self.VideoCapacityNum
        else:
            end=self.listWidget.count()
        requests=[self.state.userid,self.state.meetingid,]
        while first<end:
            item=self.listWidget.item(first)
            widget=self.listWidget.itemWidget(item)
            if widget.userid!=self.state.userid:
                requests.append(widget.userid)
            first+=1
        
        self.state.infoconn.Send(DataType.videorequest_c_to_s,requests)
    
    def listScrollrangeChanged(self,min,max):#滚动条改变长度事件,暂时没用
        # s='min:'+str(min)+'max:'+str(max)
        # print('rangechange:'+s)
        pass

    def addMember(self,info):
        item=QListWidgetItem()
        w=self.listWidget.width()
        item.setSizeHint(QSize(w, 200))  # 设置qlistwidgetitem大小
        
        widget=VideoLabel(info)
        self.listWidget.addItem(item) # 添加item
        self.listWidget.setItemWidget(item, widget) # 为item设置widget
        # index=self.listWidget.indexFromItem(item)
        return widget

    def OnMeetInfo(self,memberbytes):
        jsonstring=memberbytes
        meetinfo=eval(jsonstring)
        self.state.host=meetinfo[0]
        isMute=meetinfo[1]
        self.state.memberlist=meetinfo[2]
        self.memberwin.MemberListSignal.emit(meetinfo[2])
        num=len(self.state.memberlist)
        self.num_label.setText(str(num+1)+'人在会议中')
        for member in self.state.memberlist:
            member=MemberInfo(*member)
            self.addMember(member)
            pass
        if isMute =='1':
            self.IsMute=True
            if self.MicrophoneAction.text()=='静音':#设为静音
                if self.MicrophoneTimer.isActive():
                    self.MicrophoneTimer.stop()
                icon=QIcon(':img/麦克风-静音 1.png')
                self.MicrophoneAction.setText('开启')
                self.MicrophoneAction.setIcon(icon)      
                t='00'      
                self.state.microphone=t
                self.widget.MicrophoneChangeSignal.emit(t)       #videolabellist中的自己
                if self.state.userid==self.Mainlabel.userid:
                    self.Mainlabel.MicrophoneChangeSignal.emit(t) #主label中的自己
                self.memberwin.MicrophoneChangeSignal.emit(self.state.userid,t)  #成员列表中的自己         
                if self.ap is not None:
                    self.ap.pause()
                Toast.toast('主持人将你设为静音！')
            
    
    def getWidgetByUserId(self,userid):
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if widget.userid==userid:
                return widget
    
    def OnConnImage(self,userid,show):      
        widget=self.getWidgetByUserId(userid)
        widget.ImageSignal.emit(show)
        # if userid == self.Mainlabel.userid:
        #     self.Mainlabel.ImageSignal.emit(show)
        
    def ShowMainVideo(self,show):
        label=self.Mainlabel

        w_box=label.width()
        h_box=label.height()

        showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)

        h = showImage.height()
        w = showImage.width()

        f1 = 1.0*w_box/w
        f2 = 1.0 * h_box / h

        factor = min([f1, f2])
        width = int(w * factor)
        height = int(h * factor)    
        showImage=showImage.scaled(width,height,Qt.KeepAspectRatio)
        label.setPixmap(QPixmap.fromImage(showImage))  #打入label中
         
    def closeEvent(self, event) -> None:
        if not self.MeetIsEnd:       
            dialog=QuitWin(self)
            dialog.buttonBox.clicked.connect(self.closeAct)
            if dialog.exec_():#accept 则返回1，reject返回0
                #写界面相关      
                self.QuitSignal.emit()
                # self.close()
                event.accept()
            else:
                event.ignore() 
        else:
            event.accept()                                   
                                               
    def closeAct(self,button):
        msg=button.text()
        if msg=='离开会议':
            self.state.infoconn.Send(DataType.quitmeet_c_to_s,[self.state.userid,self.state.meetingid])
            self.vp.stop()
            self.ap.stop()
            if self.dp!=None:
                self.dp.stop()
            if self.py_record != None:
                self.py_record.stop()
            
            self.state.audiovideoconn.stop()
            
        elif msg=='结束会议':
            self.state.infoconn.Send(DataType.endmeet_c_to_s,[self.state.userid,self.state.meetingid])
            self.vp.stop()
            self.ap.stop()
            if self.dp!=None:
                self.dp.stop()
            if self.py_record != None:
                self.py_record.stop()
            self.state.audiovideoconn.stop()

class HandUpListWidget(QWidget):
    dataSignal=pyqtSignal(list)
    def __init__(self):
        super().__init__()
        self.ismoving = False
        self.resize(300, 400)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.Tool|Qt.WindowCloseButtonHint)       # 窗体置顶，去任务栏图标 加关闭按钮
        self.initUi()
        
        self.dataSignal.connect(self.UpdateList)

    def UpdateList(self,data):
        self.listWidget.clear()
        if len(data):
            self.listWidget.addItems(data)

    def initUi(self):
        self.setWindowTitle('举手列表')
        self.verticalLayout = QtWidgets.QVBoxLayout(self)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(0)
        self.listWidget = QtWidgets.QListWidget(self)
        font = QtGui.QFont()
        font.setPointSize(14)
        self.listWidget.setFont(font)
        self.verticalLayout.addWidget(self.listWidget)

    #region 鼠标移动相关
    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.ismoving = True
            self.start_point = e.globalPos()
            self.window_point = self.frameGeometry().topLeft()

    def mouseMoveEvent(self, e):
        if self.ismoving:
            relpos = e.globalPos() - self.start_point  # QPoint 类型可以直接相减
            self.move(self.window_point + relpos)      # 所以说 Qt 真是赞！

    def mouseReleaseEvent(self, e):
        self.ismoving = False
    #endregion


class MemberListWin(QWidget): #浮动成员列表，带全体静音按钮的
    VolumSignal=pyqtSignal(str,int)
    CameraChangeSignal=pyqtSignal(str,str)
    MicrophoneChangeSignal=pyqtSignal(str,str)
    AddMemberSignal=pyqtSignal(list)
    MemberQuitSignal=pyqtSignal(str)
    MemberListSignal=pyqtSignal(list)
    AllMuteSignal=pyqtSignal()
    UnAllMuteSignal=pyqtSignal()
    def __init__(self,state=None):
        super().__init__()
        self.state=state
        self.initui()
        #自己先加入
        self.addMember([self.state.userid,self.state.username,self.state.microphone,self.state.camera])

        # self.InitList(state.memberlist)
        self.VolumSignal.connect(self.OnVolum)
        self.CameraChangeSignal.connect(self.OnCamera)
        self.MicrophoneChangeSignal.connect(self.OnMicrophone)
        self.AddMemberSignal.connect(self.OnAddMember)
        self.MemberQuitSignal.connect(self.OnMemberQuit)
        self.MemberListSignal.connect(self.OnMemberList)
        self.AllMuteSignal.connect(self.OnAllMute)
        self.UnAllMuteSignal.connect(self.OnUnAllMute)

        if self.state.userid == self.state.host:
            self.pushButton.clicked.connect(self.AllmuteAct)
            self.pushButton_2.clicked.connect(self.UnAllmuteAct)
    
    def OnUnAllMute(self):
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if self.state.host != widget.userid:
                widget.MicrophoneSignal.emit('10')
           
    def OnAllMute(self):
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if self.state.host != widget.userid:
                widget.MicrophoneSignal.emit('00')

    def AllmuteAct(self):
        self.state.infoconn.Send(DataType.allmute_c_to_s,[self.state.userid,self.state.meetingid])
        # 把所有人麦克风图标改为静音
        self.OnAllMute()
        Toast.toast('已经设为全体静音！')
    
    def UnAllmuteAct(self):
        self.state.infoconn.Send(DataType.unallmute_c_to_s,[self.state.userid,self.state.meetingid])
        self.OnUnAllMute()
        Toast.toast('已经解除全体静音！')




    def getWidgetByUserid(self,userid):
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if widget.userid==userid:
                return widget

    def OnVolum(self,userid,volum):
        widget=self.getWidgetByUserid(userid)
        widget.VolumSignal.emit(volum)
   
    def OnCamera(self,userid,camera):
        widget=self.getWidgetByUserid(userid)
        widget.CameraSignal.emit(camera)
    
    def OnMicrophone(self,userid,microphone):
        widget=self.getWidgetByUserid(userid)
        widget.MicrophoneSignal.emit(microphone)
    
    def OnAddMember(self,userinfo):
        self.addMember(userinfo)
        self.state.memberlist.append(userinfo)
    
    def OnMemberQuit(self,userid):
        #region删除用户列表
        l=len(self.state.memberlist)
        for i in range(l):
            if self.state.memberlist[i][0]==userid:
                self.state.memberlist.pop(i)
                break
        #endregion
        #region 删除listwidget中
        n=self.listWidget.count()
        for i in range(0,n):
            item=self.listWidget.item(i)
            widget=self.listWidget.itemWidget(item)
            if widget.userid==userid:
                self.listWidget.takeItem(i)
                self.listWidget.removeItemWidget(item)
                break
        #endregion
       
        pass
    
    def addMember(self,info):
        member=MemberInfo(*info)
        widget=memberWidget(member)
        item=QListWidgetItem()
        w=self.listWidget.width()
        item.setSizeHint(QSize(w, 50))  # 设置qlistwidgetitem大小
        
        self.listWidget.addItem(item) # 添加item
        self.listWidget.setItemWidget(item, widget) # 为item设置widget

    def OnMemberList(self,memberlist):
        for i in range(0,len(memberlist)):
            self.addMember(memberlist[i])

    def initui(self):
        self.setMaximumSize(350,2000)
        self.setMinimumSize(350,200)  
        self.vLayout = QtWidgets.QVBoxLayout(self)
        self.vLayout.setContentsMargins(0, 0, 0, 18)
        self.listWidget = QtWidgets.QListWidget(self)
        self.vLayout.addWidget(self.listWidget)
        self.setStyleSheet('border-width: 0px;')
        self.listWidget.setStyleSheet('border: none;')
        if self.state.host is not None and  self.state.userid == self.state.host: #如果是主持人
            self.hLayout = QtWidgets.QHBoxLayout()
            self.hLayout.setContentsMargins(22, 0, 22, 0)
            self.hLayout.setSpacing(41)
            
            #region 全体静音按钮
            self.pushButton = QtWidgets.QPushButton(self)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            self.pushButton.setSizePolicy(sizePolicy)
            self.pushButton.setMinimumSize(QtCore.QSize(0, 39))
            font = QtGui.QFont()
            font.setPointSize(12)
            self.pushButton.setFont(font)
            self.hLayout.addWidget(self.pushButton)
            self.pushButton.setText("全体静音")
            #endregion

            #region 解除全体静音按钮
            self.pushButton_2 = QtWidgets.QPushButton(self)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Preferred, QtWidgets.QSizePolicy.Fixed)
            self.pushButton_2.setSizePolicy(sizePolicy)
            self.pushButton_2.setMinimumSize(QtCore.QSize(0, 39)) 
            self.pushButton_2.setFont(font)
            self.hLayout.addWidget(self.pushButton_2)
            self.pushButton_2.setText("解除全体静音")
            #endregion
          
            self.vLayout.addLayout(self.hLayout)
        
            
class ChangeInfoWindow(QWidget,Ui_ChangeInfo):    
    changenameSignal=pyqtSignal(list)
    def __init__(self,state, parent=None):
        super(ChangeInfoWindow, self).__init__(parent)
        self.setupUi(self)   
        self.state=state
        self.lineEdit.setText(self.state.username)
        self.pushButton.clicked.connect(self.ChangeNameAct)
        self.pushButton_2.clicked.connect(self.ChangePwdAct)

        self.state.infoconn.ChangeNameSignal.connect(self.changenameSignal)
        self.state.infoconn.ChangePwdSignal.connect(self.OnChangePwd)
        self.changenameSignal.connect(self.OnChangeName)

    def readConfig(self,key1,key2):
        config = configparser.ConfigParser()
        config.read('config.ini')
        return config[key1][key2]

    def writeConfig(self,data,key1,key2):
        config = configparser.ConfigParser()
        config.read('config.ini')
        config.set(key1, key2, data) 
        config.write(open("config.ini", "r+", encoding="utf-8"))

    def getRandomstr(self):
        num = random.randint(00000000,99999999)
        numstr=str(num)
        return numstr

    def ChangePwdAct(self):
        oldpwd=self.lineEdit_2.text()
        newpwd=self.lineEdit_3.text()
        newpwd2=self.lineEdit_4.text()
        if oldpwd!='' :
            if newpwd != newpwd2:
                Toast.toast('两次密码不一致！')
                return
            if not self.Check(newpwd):
                Toast.toast('新密码不符合规范！应为字母、数字或下划线，且长度大于3位！')
                return
            if newpwd==oldpwd:
                Toast.toast('新密码不应和旧密码相同！')
                return
            secretKey=self.readConfig('login_info','secret_key')
            if secretKey =='':
                secretKey=self.getRandomstr()
                self.writeConfig(secretKey,'login_info','secret_key')
            oldpwd=DES.AES_Encrypt(oldpwd,secretKey)
            newpwd=DES.AES_Encrypt(newpwd,secretKey)

            self.state.infoconn.Send(DataType.changepwd_c_to_s,[self.state.userid,oldpwd,newpwd])
        else:
            Toast.toast('请先填写旧密码！')
        if newpwd!='' or newpwd2!='':
            Toast.toast('若修改密码请先填写旧密码！')

    def ChangeNameAct(self):
        name=self.lineEdit.text()
        if name!='':
            if name==self.state.username:
                Toast.toast('新昵称应与旧昵称不相同！')
                return
            if len(name)>0:
                self.state.infoconn.Send(DataType.changename_c_to_s,[self.state.userid,name])
            else:
                Toast.toast('昵称不能为空！')

    def OnChangeName(self,datalist):
        result=datalist[0]
        if result=='1':
            Toast.toast('修改昵称成功！')
        else:
            Toast.toast('修改昵称失败！')

    def OnChangePwd(self,datalist):
        r=datalist[0]
        if r=='1':
            Toast.toast('修改密码成功！')
        else:
            Toast.toast('修改密码失败！原密码错误！')

    def Check(self,data,l=3):
        truelist = ('A','B','C','D','E','F','G','H','I','J','K','L',
                    'M','N','O','P','Q','R','S','T','U','V','W','X','Y','Z',
                    'a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q',
                    'r','s','t','u','v','w','x','y','z',
                    '1','2','3','4','5','6','7','8','9','_')
        for i in data:
            if i not in truelist:
                return False
        if len(data)>=l:
            return True
        return False

class JoinWindow(QWidget,Ui_JoinMeet):
    JoinMeetSignal=pyqtSignal(str)
    def __init__(self,state, parent=None):
        super(JoinWindow, self).__init__(parent)
        self.setupUi(self)
        self.state=state
        self.lineEdit_2.setText(self.state.username)
        self.pushButton.clicked.connect(self.JoinMeetAct)
        self.state.infoconn.ExistMeetingSignal.connect(self.OnExistMeeting)
    def JoinMeetAct(self):
        meetid=self.lineEdit.text()
        if self.checkBox.isChecked():
            microphone='11'
        else:
            microphone='10'
        if self.checkBox_2.isChecked():
            camera='11'
        else:
            camera='10'
        self.state.infoconn.Send(DataType.existMeeting_c_to_s,[meetid,])
        
        pass
    def OnExistMeeting(self,datalist):
        meetid=datalist[0]
        result=datalist[1]
        if result=='0':
            Toast.toast('无此会议！')
        else:
            self.JoinMeetSignal.emit(meetid)
            self.hide()
   
class ChatWin(QWidget):#正在使用
    MsgSignal=pyqtSignal(str,str)
    def __init__(self,state):
        super().__init__()
        self.state=state
        self.MsgSignal.connect(self.OnMsg)
        self.initui()
    def initui(self):
        self.hlayout=QHBoxLayout()
        self.vlayout=QVBoxLayout()
        self.vlayout.setSpacing(0)
        self.vlayout.setContentsMargins(0, 0, 0, 0)
        self.hlayout.setContentsMargins(0, 0, 0, 0)

        self.textEdit=QTextEdit()
        self.textEdit.setReadOnly(True)
        self.vlayout.addWidget(self.textEdit,4)

        self.textEdit2=QTextEdit()  
        self.vlayout.addWidget(self.textEdit2,1)
        self.textEdit2.setStyleSheet('background-color:rgb(255,255,255)')
        self.textEdit.setStyleSheet('background-color:rgb(248,249,251)')
        spacerItem = QtWidgets.QSpacerItem(40, 20, QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Minimum)
        self.hlayout.addItem(spacerItem)

        self.button=QPushButton('发送')
        font = QtGui.QFont()
        font.setPointSize(10)
        self.button.setFont(font)
        self.button.setSizePolicy(QSizePolicy.Fixed,QSizePolicy.Fixed)
        # self.button.setMaximumSize(100,50)
        self.button.setMinimumSize(100,50)
        self.hlayout.addWidget(self.button)
        self.vlayout.addLayout(self.hlayout)
        self.setLayout(self.vlayout)
        self.setMaximumSize(350,2000)
        self.setMinimumSize(350,200)
        self.button.clicked.connect(self.sendAct)
    
    def sendAct(self):
        msg=self.textEdit2.toPlainText()
        name=self.state.username
        if msg!='':
            self.showMsg(name,msg,True)     
            self.state.infoconn.Send(DataType.msg_c_to_s,[self.state.userid,self.state.meetingid,msg])
            self.textEdit2.setText('')
        else:
            Toast.toast('发送消息不能为空！')

    def OnMsg(self,name,msg):
        self.showMsg(name,msg)

    def showMsg(self,name,msg,flag=False):
        if flag:
            nameformat=self.format((4,215,148),size=11)
        else:
            nameformat=self.format((4,215,148),size=11)
        msgformat=self.format((0,0,0),size=11)
        self.textEdit.setCurrentCharFormat(nameformat)
        self.textEdit.append(name)
        self.textEdit.setCurrentCharFormat(msgformat)
        self.textEdit.append(msg)

    def format(self,color,size='10',style=''):
        """Return a QTextCharFormat with the given attributes.
        """    
        _color = QColor(*color)
        # _color.setNamedColor(color)

        _format = QTextCharFormat()
        _format.setForeground(_color)
        font = QtGui.QFont()
        if 'bold' in style:
            font.setBold(True)
        if 'italic' in style:
            font.setItalic(True)
        font.setFamily("Arial")
        font.setPointSize(size)
        _format.setFont(font)
        return _format

class EndMeetWin(QDialog):
     def __init__(self,parent=None):
        super().__init__(parent)   
        TitleLabel = QLabel("会议结束！")
        self.buttonBox = QDialogButtonBox()
        self.buttonBox.addButton("离开", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("确定", QDialogButtonBox.AcceptRole)

        self.buttonBox.accepted.connect(self.accept)
        # self.buttonBox.rejected.connect(self.reject)
       
        layout = QVBoxLayout()
        layout.addWidget(TitleLabel)
        TitleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.buttonBox)
 
        self.setLayout(layout)
        self.setWindowTitle("会议结束！")

class QuitWin(QDialog):
    def __init__(self,parent=None):
        super().__init__(parent)   
        TitleLabel = QLabel("离开会议")
   
        #“确定” “取消” 按钮 可以使用预置的 复合控件 按钮盒子
        '''
        #可以使用内置标准按钮
        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        '''
        self.buttonBox = QDialogButtonBox()
        #self.buttonBox.setOrientation(Qt.Vertical)  # 设为竖向显示，默认为水平方向
        #self.buttonBox.setStandardButtons(QDialogButtonBox.Ok|QDialogButtonBox.Cancel)
        if self.parent().state.host==self.parent().state.userid:
            self.buttonBox.addButton("结束会议", QDialogButtonBox.AcceptRole)
        self.buttonBox.addButton("取消", QDialogButtonBox.RejectRole)
        self.buttonBox.addButton("离开会议", QDialogButtonBox.AcceptRole)
        self.buttonBox.accepted.connect(self.accept)
        self.buttonBox.rejected.connect(self.reject)
        
        layout = QVBoxLayout()
        layout.addWidget(TitleLabel)
        TitleLabel.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.buttonBox)
 
        self.setLayout(layout)
        self.setWindowTitle("离开会议")

class CommonHelper:
    def __init__(self):
        self.styleFile='./qss/Ubuntu.qss'
        pass
 
    @staticmethod
    def readQss():
        styleFile='./qss/Ubuntu.qss'
        with open(styleFile, 'r') as f:
            return f.read()

#折叠所有区域代码的快捷键：ctrl+k, ctrl+0;
# 展开所有折叠区域代码的快捷键：ctrl +k, ctrl+J;
# 自动格式化代码的快捷键：ctrl+k, ctrl+f;

if __name__=='__main__':
    app=QApplication(sys.argv)
    #底部任务栏图标设置为自己的
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")

    login_window=LoginWindow()
    login_window.setStyleSheet(CommonHelper.readQss())
    mainwin=MainWindow()
    login_window.ArgsSignal.connect(mainwin.OnInit)

    if not login_window.exec_():
        sys.exit(0)
    else:
        mainwin.setStyleSheet(CommonHelper.readQss())
        mainwin.show()

    sys.exit(app.exec_())