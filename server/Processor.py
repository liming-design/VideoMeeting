import socket,threading,random
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from Structure import DataType
from Tools import HASH
from db import MyDataBase
import json
import time

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

class MyThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.__flag = threading.Event()     # 用于暂停线程的标识
        self.__flag.set()       # 设置为True
        self.__running = threading.Event()      # 用于停止线程的标识
        self.__running.set()      # 将running设置为True
        self.setDaemon(True)
 
    def pause(self):
        self.__flag.clear()     # 设置为False, 让线程阻塞

    def resume(self):
        self.__flag.set()    # 设置为True, 让线程停止阻塞

    def stop(self):
        self.__flag.set()       # 将线程从暂停状态恢复, 如何已经暂停的话
        self.__running.clear()        # 设置为False    

class UdpConnect(QObject):
    def __init__(self,port):
        super().__init__()
        self.host = socket.gethostname()#   设置IP和端口  
        ip=socket.gethostbyname(self.host)
        # print(ip)
        ip='0.0.0.0'
        # ip='10.91.0.26'
        
        self.addr=(ip,port)
       
        self.s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.bind(self.addr)
        
        self.buff=65500
        # self.listen_thread=threading.Thread(target=self.listening,args=())
        # self.listen_thread.start()

class AudioVideoConn(UdpConnect,MyThread):
    ImageSignal=pyqtSignal(list)
    AudioSignal=pyqtSignal(list)
    
    def __init__(self,selfport=1233):       
        super().__init__(selfport)
        self.mydb=MyDataBase()
        self.start()
    
    def Send(self,datatype,datalist,addr):      
        databyte=MySend(datatype,datalist)
        try:
            self.s.sendto(databyte,addr)
        except:
            pass
    
    def run(self):
        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            try:                                
                (data, addr) = self.s.recvfrom(self.buff)
            except Exception as e:
                print(e.__str__())
                break
            datalist=MyReceive(data)
            datatype=datalist[0]
            del datalist[0]
            if datatype==DataType.image_c_to_s.value:
                self.OnImage(datalist,addr)
            elif datatype==DataType.diff_image_c_to_s.value:
                self.OnDiffImage(datalist,addr)
            elif datatype==DataType.audio_c_to_s.value:
                self.OnAudio(datalist,addr)   
        self.s.close() 
        

    def OnDiffImage(self,datalist,addr):
        requestid=datalist[0].decode()
        meetingid=datalist[1].decode()
        # sqlstr='select Ip,AudioVideoPort from UserMeeting where MeetingId =? and  UserId in (select UserId from  UserVideoRequest where RequestId like ?)'
        sqlstr='select Ip,AudioVideoPort from UserMeeting where MeetingId =? and  RequestId like ?'
        useraddrs=self.mydb.SelectAll(sqlstr,[meetingid,'%'+requestid+'%',])
        del datalist[1]
        for addr in useraddrs:
            self.Send(DataType.diff_image_s_to_c,datalist,addr)            
            
    def OnImage(self,datalist,addr):
        requestid=datalist[0].decode()
        meetingid=datalist[1].decode()
        # sqlstr='select Ip,AudioVideoPort from UserMeeting where MeetingId =? and  UserId in (select UserId from  UserVideoRequest where RequestId like ?)'
        sqlstr='select Ip,AudioVideoPort from UserMeeting where MeetingId =? and RequestId like ?'
        useraddrs=self.mydb.SelectAll(sqlstr,[meetingid,'%'+requestid+'%',])
        del datalist[1]
        for addr in useraddrs:
            self.Send(DataType.image_s_to_c,datalist,addr)
        
    def OnAudio(self,datalist,addr):
        userid=datalist[0].decode()
        meetingid=datalist[1].decode()
        sqlstr='select Ip,AudioVideoPort from UserMeeting where MeetingId=? and UserId != ?'
        useraddrs=self.mydb.SelectAll(sqlstr,[meetingid,userid])
        del datalist[1]
        for addr in useraddrs: 
            self.Send(DataType.audio_s_to_c,datalist,addr)

    def stop(self):
        super().stop()
        # if getattr(ws, '_closed') == False:
      
        self.s.close() 

class InfoConn(UdpConnect,MyThread):
    LoginSignal=pyqtSignal(list)
    MeetingSignal=pyqtSignal(list)
    JoinMeetingSignal=pyqtSignal(list)
    QuitMeetingSignal=pyqtSignal(list)
    EndMeetingSignal=pyqtSignal(list)
    def __init__(self,port=1234):       
        super().__init__(port)
        self.mydb=MyDataBase()
        self.start()

    def Send(self,datatype,data,addr):      
        rdata=[]
        for t in data:
            rdata.append(t.encode())
        databyte=MySend(datatype,rdata)
        try:
            self.s.sendto(databyte,addr)
        except:
            pass
    
    def StrReceive(self,datalist,datatype):
        result=[]
        for data in datalist:
            result.append(data.decode())
        return result
             
    def run(self):
        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            try:
                (data, addr) = self.s.recvfrom(self.buff)
            except:
                break
            datalist=MyReceive(data)
            datatype=datalist[0]
            del datalist[0]
            datalist=self.StrReceive(datalist,datatype)
            if datatype==DataType.login_c_to_s.value:
                self.OnLogin(datalist,addr)
            elif datatype==DataType.meetingid_c_to_s.value:
                self.OnMeetid(datalist,addr)
            elif datatype==DataType.meetinfo_c_to_s.value:
                self.OnMeetInfo(datalist,addr)
            elif datatype==DataType.videorequest_c_to_s.value:
                self.OnVideoRequest(datalist,addr)
            elif datatype==DataType.msg_c_to_s.value:
                self.OnMsg(datalist,addr)
            elif datatype==DataType.quitmeet_c_to_s.value:
                self.OnQuitMeet(datalist)
            elif datatype==DataType.endmeet_c_to_s.value:
                self.OnEndMeet(datalist)
            elif datatype==DataType.membercamera_c_to_s.value:
                self.OnMemberCamera(datalist)
            elif datatype==DataType.membermicrophone_c_to_s.value:
                self.OnMemberMicrophone(datalist)
            elif datatype==DataType.register_c_to_s.value:
                self.OnRegister(datalist,addr)
            elif datatype==DataType.existMeeting_c_to_s.value:
                self.OnExitMeeting(datalist,addr)
            elif datatype==DataType.changename_c_to_s.value:
                self.OnChangeName(datalist,addr)
            elif datatype==DataType.changepwd_c_to_s.value:
                self.OnChangePwd(datalist,addr)
            elif datatype == DataType.handup_c_to_s.value:
                self.OnHandUp(datalist,addr)
            elif datatype == DataType.handdown_c_to_s.value:
                self.OnHandDown(datalist,addr)
            elif datatype == DataType.allmute_c_to_s.value:
                self.OnAllMute(datalist,addr)
            elif datatype == DataType.unallmute_c_to_s.value:
                self.OnUnAllMute(datalist,addr)      
        self.s.close()   
     
    def stop(self):
        super().stop()
        self.s.close() 
    
    def OnAllMute(self,datalist,addr):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select InitiatorId from Meeting where MeetingId = ?'
        row=self.mydb.SelectOne(sqlstr,[meetingid])
        InitiatorId=row[0]
        if InitiatorId == userid:
            sqlstr='update Meeting set IsMute = 1 where MeetingId=?'
            self.mydb.Execute(sqlstr,[meetingid])

            sqlstr='update UserMeeting set Microphone=?  where MeetingId=? and userid !=?'
            self.mydb.Execute(sqlstr,['00',meetingid,userid])

            self.broadcast(DataType.allmute_s_to_c,[],userid,meetingid)


    def OnUnAllMute(self,datalist,addr):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select InitiatorId from Meeting where MeetingId = ?'
        row=self.mydb.SelectOne(sqlstr,[meetingid])
        InitiatorId=row[0]
        if InitiatorId == userid: #如果是支持人发出的
            sqlstr='update Meeting set IsMute = 0 where MeetingId=?'
            self.mydb.Execute(sqlstr,[meetingid])
            
            sqlstr='update UserMeeting set Microphone=? where MeetingId=? and userid !=?'
            self.mydb.Execute(sqlstr,['10',meetingid,userid])

            self.broadcast(DataType.unallmute_s_to_c,[],userid,meetingid)

    def OnHandUp(self,datalist,addr):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select 1 from HandUpList where UserId=? and MeetingId=?'
        result=self.mydb.Exists(sqlstr,[userid,meetingid])
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        if result:# 说明存在此人，则什么也不用做
            pass
            # sqlstr='update HandUpList set Time = ? where UserId=? and MeetingId=?'
            # self.mydb.Execute(sqlstr,[nowtime,userid,meetingid])
        else:
            sqlstr='insert into HandUpList(UserId,MeetingId,Time) values(?,?,?)'
            self.mydb.Execute(sqlstr,[userid,meetingid,nowtime])
            self.SendHandUpList(meetingid)

    def OnHandDown(self,datalist,addr):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='select 1 from HandUpList where UserId=? and MeetingId=?'
        result=self.mydb.Exists(sqlstr,[userid,meetingid])
        if result:
            sqlstr='delete from HandUpList where UserId=? and MeetingId=?'
            result=self.mydb.Execute(sqlstr,[userid,meetingid])
            self.SendHandUpList(meetingid)
    
    def SendHandUpList(self,meetingid): 
        sqlstr='select InitiatorId from Meeting where MeetingId = ?'
        row=self.mydb.SelectOne(sqlstr,[meetingid])
        InitiatorId=row[0]

        sqlstr='select Ip,InfoPort from UserMeeting where MeetingId=? and UserId = ?'
        addr=self.mydb.SelectOne(sqlstr,[meetingid,InitiatorId])
        
        if len(addr):
            sqlstr='select User.UserName from User,HandUpList where HandUpList.MeetingId=? and HandUpList.UserId = User.UserId'
            result=self.mydb.SelectAll(sqlstr,[meetingid,])
            datalist=[]
            if result !=[] and result is not None:
                for i in result:
                    datalist.append(i[0])
            self.Send(DataType.handuplist_s_to_c,datalist,addr)

   

    def OnChangeName(self,datalist,addr):
        userid=datalist[0]
        name=datalist[1]
        sqlstr='update User set UserName=? where UserId=?'
        result=self.mydb.Execute(sqlstr,[name,userid])
        if result:
            self.Send(DataType.changename_s_to_c,['1',name],addr)
        else:
            self.Send(DataType.changename_s_to_c,['0'],addr)

    def OnChangePwd(self,datalist,addr):
        userid=datalist[0]
        oldpwd=datalist[1]
        newpwd=datalist[2]
        myhash=HASH()
        hasholdpwd=myhash.HashSha256(oldpwd)
        hashnewpwd=myhash.HashSha256(newpwd)
        sqlstr='select 1 from User where UserId=? and Pwd=?'
        result=self.mydb.Exists(sqlstr,[userid,hasholdpwd])
        if result:
            sqlstr='update User set Pwd=? where UserId=?'
            self.mydb.Execute(sqlstr,[hashnewpwd,userid])
            self.Send(DataType.changepwd_s_to_c,['1',],addr)
        else:
            self.Send(DataType.changepwd_s_to_c,['0',],addr)

    def OnExitMeeting(self,datalist,addr):
        meetingid=datalist[0]
        sqlstr='select 1 from Meeting where MeetingId = ?'
        result=self.mydb.Exists(sqlstr,[meetingid,])
        if result:
            self.Send(DataType.existMeeting_s_to_c,[meetingid,'1'],addr)
        else:
            self.Send(DataType.existMeeting_s_to_c,[meetingid,'0'],addr)

    def OnRegister(self,datalist,addr):
        name=datalist[0]
        pwd=datalist[1]
        def getRandomstr():
            num = random.randint(00000000,99999999)
            numstr=str(num)
            return numstr

        userid=getRandomstr()
        sqlstr='select * from User where UserId=? '
        
        while self.mydb.Exists(sqlstr,[userid,]):
            userid=self.getRandomstr()
        sqlstr='insert into User(UserId,UserName,Pwd) values (?,?,?)'
        myhash=HASH()
        hashpwd=myhash.HashSha256(pwd)
        self.mydb.Execute(sqlstr,[userid,name,hashpwd])    
        self.Send(DataType.register_s_to_c,[userid],addr)

    def OnMemberMicrophone(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        microphone=datalist[2]
        sqlstr='update UserMeeting set Microphone=? where UserId=? and MeetingId=?'
        self.mydb.Execute(sqlstr,[microphone,userid,meetingid])
        self.broadcast(DataType.membermicrophone_s_to_c,[userid,microphone],userid,meetingid)
    
    def OnMemberCamera(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        camera=datalist[2]
        sqlstr='update UserMeeting set Camera=? where UserId=? and MeetingId=?'
        self.mydb.Execute(sqlstr,[camera,userid,meetingid])
        self.broadcast(DataType.membercamera_s_to_c,[userid,camera],userid,meetingid)

    def OnEndMeet(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        self.broadcast(DataType.endmeet_s_to_c,[],userid,meetingid)
        sqlstr='delete from UserMeeting where  MeetingId=?'
        result=self.mydb.Execute(sqlstr,[meetingid])
        sqlstr='delete from HandUpList where MeetingId=?'
        result=self.mydb.Execute(sqlstr,[meetingid])
        self.EndMeetingSignal.emit([userid,meetingid])


    def OnQuitMeet(self,datalist):
        userid=datalist[0]
        meetingid=datalist[1]
        sqlstr='delete from UserMeeting where UserId=? and MeetingId=?'
        result=self.mydb.Execute(sqlstr,[userid,meetingid])
        self.broadcast(DataType.memberquit_s_to_c,[userid],userid,meetingid)
        self.QuitMeetingSignal.emit([userid,meetingid])
    
    def broadcast(self,datatype,datalist,userid,meetingid):
        sqlstr='select Ip,InfoPort from UserMeeting where MeetingId=? and UserId != ?'
        useraddr=self.mydb.SelectAll(sqlstr,[meetingid,userid])
        for addr in useraddr:
            self.Send(datatype,datalist,addr)

    def OnMsg(self,datalist,addr):
        userid=datalist[0]
        meetingid=datalist[1]
        msg=datalist[2]
        sqlstr='select UserName from User where UserId=?'
        row=self.mydb.SelectOne(sqlstr,[userid])
        username=row[0]
        sqlstr='select Ip,InfoPort from UserMeeting where MeetingId=? and UserId != ?'
        useraddr=self.mydb.SelectAll(sqlstr,[meetingid,userid])
        for addr in useraddr:
            self.Send(DataType.msg_s_to_c,[username,msg],addr)

    def OnVideoRequest(self,datalist,addr):
        userid=datalist[0]
        meetingid=datalist[1]
        # sqlstr='update UserVideoRequest set RequestId=? where UserId=?'
        sqlstr='update UserMeeting set RequestId=? where UserId=? and MeetingId=?'
        ids=''
        for i in range(2,len(datalist)):
            ids+=datalist[i]
            ids+=';'
        self.mydb.Execute(sqlstr,[ids,userid,meetingid])
        pass
    
    def OnMeetInfo(self,datalist,addr):
        meetid=datalist[0]
        userid=datalist[1]
        Microphone=datalist[2]
        Camera=datalist[3]
        audiovideoport=int(datalist[4])
        
        #region查找会议信息
        sqlstr='select InitiatorId from Meeting where MeetingId = ?'
        row=self.mydb.SelectOne(sqlstr,[meetid])
        
        InitiatorId=row[0]
        # result={'host':InitiatorId}
        result=[InitiatorId,]

        # 检查是否全体静音
        sqlstr='select IsMute from Meeting where MeetingId=?'
        ans = self.mydb.SelectOne(sqlstr,[meetid,])
        isMute='0'
        if ans is not None and ans[0]==1:
            Microphone='00'
            isMute='1'
        result.append(isMute)
        #endregion
        
        #region查找成员信息
        sqlstr="select User.UserId,User.UserName,Microphone,Camera,Ip,InfoPort from User,UserMeeting \
            where MeetingId=? and UserMeeting.UserId = User.UserId and User.UserId!=?"
        members=self.mydb.SelectAll(sqlstr,[meetid,userid])   
        #endregion
        
        #region 发送成员列表
        memberlist=[]
        for member in members :
            # t={'userid':member[0],'username':member[1],'microphone':member[2],'camera':member[3]}
            t=[member[0],member[1],member[2],member[3]]
            memberlist.append(t)
        result.append(memberlist)
        json_string = json.dumps(result)
        self.Send(DataType.meetinfo_s_to_c,[json_string,],addr)
        #endregion

        #region 拼接requestid
        videorequest=''
        end=3
        if len(members)<3: end=len(members)
        for i in range(0,end):
            memberid=members[i][0]
            videorequest+=memberid
            videorequest+=';'
        #endregion       

        #region向usermeeting中插入数据
        
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))
        sqlstr='insert into UserMeeting(UserId,MeetingId,EntryTime,Microphone,Camera,Ip,InfoPort,AudioVideoPort,RequestId) values (?,?,?,?,?,?,?,?,?)'
        self.mydb.Execute(sqlstr,[userid,meetid,nowtime,Microphone,Camera,addr[0],addr[1],audiovideoport,videorequest])
        #endregion
        
        #region 向所有成员发送adduser消息
        sqlstr='select UserName from User where UserId=?'
        username=self.mydb.SelectOne(sqlstr,[userid])[0]
        t=[userid,username,Microphone,Camera]
        for member in members :
            addr=(member[4],member[5])
            self.Send(DataType.add_member_s_to_c,t,addr)
        #endregion
        self.JoinMeetingSignal.emit([userid,username,meetid])
    
    def OnLogin(self,datalist,addr):
        userId=datalist[0]
        pwd=datalist[1]

        myhash=HASH()
        hashpwd=myhash.HashSha256(pwd)

        sqlstr='select UserName from User where UserId=? and Pwd=?'
        
        if self.mydb.Exists(sqlstr,[userId,hashpwd]):
            row=self.mydb.SelectOne(sqlstr,[userId,hashpwd])
            username=row[0]
            self.Send(DataType.login_s_to_c,['1',username],addr)
            self.LoginSignal.emit([userId,username])
        else:
            self.Send(DataType.login_s_to_c,['0'],addr)            

    def OnMeetid(self,datalist,addr):     
        def getRandomstr():
            num = random.randint(00000000,99999999)
            numstr=str(num)
            return numstr

        meetingid=getRandomstr()
        sqlstr='select * from Meeting where MeetingId=? '
        
        while self.mydb.Exists(sqlstr,[meetingid,]):
            meetingid=self.getRandomstr()
        
        userid=datalist[0]
        Microphone=datalist[1]
        Camera=datalist[2]
        nowtime=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        sqlstr='insert into Meeting(MeetingId,InitiatorId,StartTime,Number) values (?,?,?,?)'
        result=self.mydb.Execute(sqlstr,[meetingid,userid,nowtime,1])
        
        self.Send(DataType.meetingid_s_to_c,[meetingid,],addr)   
        self.MeetingSignal.emit([userid,meetingid])

