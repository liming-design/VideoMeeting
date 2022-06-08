
import socket
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
import random
import cv2
import numpy as np
import threading
import wave
import pyaudio
from datetime import datetime
import time
from numpy import array
from moviepy.editor import AudioFileClip,VideoFileClip
import os
from PIL import ImageGrab
import configparser
from Structure import DataType
from Tools import VideoConvert

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

def readConfig(key1,key2):
    config = configparser.ConfigParser()
    config.read('config.ini')
    return config[key1][key2]

def MySend(datatype,DataList):
    result=bytearray(1)
    result[0]=datatype.value
    for databyte in DataList:
        num=len(databyte)
        l=num.to_bytes(4,byteorder='little')
        result+=l
        result+=databyte
        # result = np.vstack((result,databyte))
        # result.append(databyte)
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

class DesktopProcessor(QObject,MyThread):
    ImageSignal=pyqtSignal(np.ndarray)
    def __init__(self,state) -> None: 
        super().__init__()       
        self.state=state
        self.userid=self.state.userid
        self.useridbytes=self.state.userid.encode()
        self.meetidbytes=self.state.meetingid.encode()
        self.start()

    def run(self):
        # success, frame=self.cap.read()#读取视频流 
        
        show1 = np.asarray(ImageGrab.grab())#截图

        # show1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # showImage = QImage(show1.data, show1.shape[1], show1.shape[0], QImage.Format_RGB888)

        self.ImageSignal.emit(show1)

        encodeshow1=VideoConvert.JpegCompress(show1)
        decodeshow1=VideoConvert.UnCompress(encodeshow1)

        imbyt=encodeshow1.tobytes()
        self.state.audiovideoconn.Send(DataType.image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])     

        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            
            # success, frame=self.cap.read()#读取视频流        
            # if  success:   
            # show2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   
            show2 = np.asarray(ImageGrab.grab())#截图

            self.ImageSignal.emit(show2)

            encodeshow2=VideoConvert.JpegCompress(show2)
            decodeshow2=VideoConvert.UnCompress(encodeshow2)

            diffshow=cv2.bitwise_xor(decodeshow1,decodeshow2)
            if (diffshow == 0).all():   continue
            encodediff=VideoConvert.PngCompress(diffshow)

            if len(encodediff) < len(encodeshow2):# 传差异化图像
                imbyt=encodediff.tobytes()
                self.state.audiovideoconn.Send(DataType.diff_image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])     
            else:
                imbyt=encodeshow2.tobytes()#全传
                self.state.audiovideoconn.Send(DataType.image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])     
            
            decodeshow1= decodeshow2  
            # else: 
            #     break  
            time.sleep(0.04)

class VideoProcessor(QObject,MyThread):
    ImageSignal=pyqtSignal(np.ndarray)
    def __init__(self,state) -> None: 
        super(VideoProcessor, self).__init__()       
        self.state=state
        
        camera=readConfig('camera','interface')
        if camera.isalnum():
            camera=int(camera)
         
        self.cap = cv2.VideoCapture(camera)
        self.userid=self.state.userid
        self.useridbytes=self.state.userid.encode()
        self.meetidbytes=self.state.meetingid.encode()
        self.start()
  
    #region run1 捕获自己图像
    # def run(self):
    #     success, frame=self.cap.read()#读取视频流 
        
    #     show1 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    #     # showImage = QImage(show1.data, show1.shape[1], show1.shape[0], QImage.Format_RGB888)

    #     self.ImageSignal.emit(show1)

    #     encodeshow1=VideoConvert.JpegCompress(show1)
    #     decodeshow1=VideoConvert.UnCompress(encodeshow1)

    #     imbyt=encodeshow1.tobytes()
    #     self.state.audiovideoconn.Send(DataType.image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])     

    #     while self._MyThread__running.isSet():
    #         self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            
    #         success, frame=self.cap.read()#读取视频流        
    #         if  success:   
    #             show2 = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   
    #             # showImage = QImage(show2.data, show2.shape[1], show2.shape[0], QImage.Format_RGB888)

    #             self.ImageSignal.emit(show2)

    #             encodeshow2=VideoConvert.JpegCompress(show2)
    #             decodeshow2=VideoConvert.UnCompress(encodeshow2)

    #             diffshow=cv2.bitwise_xor(decodeshow1,decodeshow2)
    #             if (diffshow == 0).all():   continue
    #             encodediff=VideoConvert.PngCompress(diffshow)
                

    #             if len(encodediff) < len(encodeshow2):# 传差异化图像
    #                 imbyt=encodediff.tobytes()
    #                 self.state.audiovideoconn.Send(DataType.diff_image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])     
    #             else:
    #                 imbyt=encodeshow2.tobytes()#全传
    #                 self.state.audiovideoconn.Send(DataType.image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])     
                
    #             decodeshow1= decodeshow2  
    #         else: 
    #             break  
    #         time.sleep(0.04)
    #     self.cap.release()
    #endregion

    #region run2
    def run(self): 
        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回   
            success, frame=self.cap.read()#读取视频流 
            if  success:             
                show = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)   
                self.ImageSignal.emit(show)
                encodeshow=VideoConvert.JpegCompress(show)
                imbyt=encodeshow.tobytes()#全传
                self.state.audiovideoconn.Send(DataType.image_c_to_s,[self.useridbytes,self.meetidbytes,imbyt])  
            else: break    
            time.sleep(0.04)
        self.cap.release()
    #endregion
class AudioProcessor(QObject,MyThread):
    talkingSignal=pyqtSignal(str,int)
    def __init__(self,state) -> None:    
        super().__init__()  
        self.chunk_size = 1024  # 512
        self.buff=1024
        self.audio_format = pyaudio.paInt16
        self.channels = 1
        self.rate = 20000
        self.save_count=0

        self.p = pyaudio.PyAudio()
        self.playing_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate, output=True,
                                          frames_per_buffer=self.chunk_size)
        
        self.recording_stream = self.p.open(format=self.audio_format, channels=self.channels, rate=self.rate, input=True,
                                            frames_per_buffer=self.chunk_size)

        self.state=state
        self.state.audiovideoconn.AudioSignal.connect(self.receive_server_data)

        # self.send_thread=threading.Thread(target=self.send_data_to_server,args=()).start()
        self.start()
 
    def receive_server_data(self,userid,string_audio_data):
        self.playing_stream.write(string_audio_data)
        audio_data = np.frombuffer(string_audio_data, dtype='int16') 
        max=np.max(audio_data)
        self.talkingSignal.emit(userid,max)

    def run(self):
        LEVEL = 1500            # 声音保存的阈值
        COUNT_NUM = 20          # NUM_SAMPLES个取样之内出现COUNT_NUM个大于LEVEL的取样则记录声音
        SAVE_LENGTH = 8         # 声音记录的最小长度：SAVE_LENGTH * NUM_SAMPLES 个取样
        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            string_audio_data = self.recording_stream.read(self.buff)
            # 将读入的数据转换为数组
            audio_data = np.frombuffer(string_audio_data, dtype='int16') 
            # 计算大于LEVEL的取样的个数
            large_sample_count = np.sum( audio_data > LEVEL ) 
            # print (np.max(audio_data) )
            max=np.max(audio_data)
             # 如果个数大于COUNT_NUM，则至少发送SAVE_LENGTH个块
            if large_sample_count > COUNT_NUM: 
                self.save_count = SAVE_LENGTH 
            else: 
                self.save_count -= 1 
            if self.save_count < 0: 
                self.save_count = 0 

            if self.save_count > 0: 
            # 将要保存的数据存放到save_buffer中
                userid=self.state.userid.encode()
                meetingid=self.state.meetingid.encode()
                self.state.audiovideoconn.Send(DataType.audio_c_to_s,[userid,meetingid,string_audio_data])
                self.talkingSignal.emit(self.state.userid,max)
            else:
                continue
        self.recording_stream.stop_stream()
        self.recording_stream.close()
        self.p.terminate()
   
    #region 关闭麦克风关不干净
    # def pause(self): 
    #     self.save_count=0
    #     super().pause()
    #     self.recording_stream.stop_stream()
    #     self.recording_stream.close()
    #     # self.p1.terminate()

    # def resume(self):
    #     # self.recording_stream.start_stream()
    #     self.p1 = pyaudio.PyAudio()
    #     self.recording_stream = self.p1.open(format=self.audio_format, channels=self.channels, rate=self.rate, input=True,
    #                                         frames_per_buffer=self.chunk_size)
    #     self.save_count=0
    #     super().resume()
    #endregion
 
class UdpConnect(QObject):
    def __init__(self,selfport):
        super(UdpConnect, self).__init__()
        self.selfport=self.getRandomPort()
        self.addr=('0.0.0.0',self.selfport)
        # self.addr=('127.0.0.1',self.selfport)
        
        serverip=readConfig('server','ip')
        # serverip='10.91.0.168'
        # serverip='10.91.0.26'
        # serverip='169.254.157.172'
        
        self.ServerInfoAddr=(serverip,1234)
        self.ServerAvAddr=(serverip,1233)
        
        self.buff=65500
        self.s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        self.s.bind(self.addr)
       
        # self.ReceiveThread=threading.Thread(target=self.Receiving,args=())
        # self.ReceiveThread.start()
    def ReStart(self):

        # self.s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.s.bind(self.addr)

    def getRandomSocket(self):
        s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        selfport = self.getRandomPort()
        s.bind(('127.0.0.1',self.selfport))
        return s

    def getRandomPort(self):
        result = False
        while result==False:
            port = random.randint(1024,65535)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            try:
                sock.bind(("0.0.0.0", port))
                result = True
            except:
                pass
            sock.close()
        return port
    
class AudioVideoConn(UdpConnect,MyThread):
    ImageSignal=pyqtSignal(str,np.ndarray)
    AudioSignal=pyqtSignal(str,bytes)
    
    def __init__(self,selfport=1001):       
        super().__init__(selfport)
        self.start()
    
    def Send(self,datatype,data):
        databyte=MySend(datatype,data)
        try:
            self.s.sendto(databyte,self.ServerAvAddr)
        except Exception as e:
            print(e.__str__())
            return

    def run(self): 
        oldimagebytes=None
        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            try:
                (data, addr) = self.s.recvfrom(self.buff)
            except:
                break
            datalist=MyReceive(data)
            datatype=datalist[0]
            del datalist[0]
            if datatype==DataType.image_s_to_c.value:
                oldimagebytes=datalist[1]
                self.OnImage(datalist)
            elif datatype==DataType.diff_image_s_to_c.value:
                self.OnDiffImage(oldimagebytes,datalist)    
            elif datatype==DataType.audio_s_to_c.value:
                self.OnAudio(datalist)
        
    def OnDiffImage(self,oldimagebytes,datalist):
        if oldimagebytes != None:
            userid=datalist[0].decode()
            imagebytes=datalist[1]
            encodeshow = np.frombuffer(imagebytes, dtype=np.uint8)#从opencv的字节码中解包到numpy数组里
            diffshow=VideoConvert.UnCompress(encodeshow)

            encodeshow = np.frombuffer(oldimagebytes, dtype=np.uint8)#从opencv的字节码中解包到numpy数组里
            show1=VideoConvert.UnCompress(encodeshow)

            show2=cv2.bitwise_xor(show1,diffshow)
            # showImage = QImage(show2.data, show2.shape[1], show2.shape[0], QImage.Format_RGB888)
            self.ImageSignal.emit(userid,show2)

    def OnAudio(self,datalist):
        userid=datalist[0].decode()
        string_audio_data=datalist[1]
        self.AudioSignal.emit(userid,string_audio_data)
        pass
    
    def OnImage(self,datalist):
        userid=datalist[0].decode()
        imagebytes=datalist[1]
        encodeshow = np.frombuffer(imagebytes, dtype=np.uint8)#从opencv的字节码中解包到numpy数组里
        show=VideoConvert.UnCompress(encodeshow)
        # showImage = QImage(show.data, show.shape[1], show.shape[0], QImage.Format_RGB888)
        self.ImageSignal.emit(userid,show)
        pass
    
    def stop(self):
        super().stop()
        self.s.close()

class InfoConn(UdpConnect,MyThread):
    LoginSignal=pyqtSignal(list)
    MeetidSignal=pyqtSignal(str)
    MeetInfoSignal=pyqtSignal(str)
    AddMemberSignal=pyqtSignal(list)
    DelMemberSignal=pyqtSignal(str)
    MsgSignal=pyqtSignal(list)
    QuitMeetSignal=pyqtSignal(str)
    EndMeetSignal=pyqtSignal()
    MemberCameraSignal=pyqtSignal(list)
    MemberMicrophoneSignal=pyqtSignal(list)
    RegisterSignal=pyqtSignal(list)
    ExistMeetingSignal=pyqtSignal(list)
    ChangeNameSignal=pyqtSignal(list)
    ChangePwdSignal=pyqtSignal(list)
    HandUpListSignal=pyqtSignal(list)
    AllMuteSignal=pyqtSignal()
    UnAllMuteSignal=pyqtSignal()

    def __init__(self,selfport=1000):       
        super().__init__(selfport)
        self.start()

    def Send(self,datatype,data):   
        rdata=[]
        for t in data:
            rdata.append(t.encode())
        data=rdata

        databyte=MySend(datatype,data)
        self.s.sendto(databyte, self.ServerInfoAddr)

    # def LoginSend(self,datatype,data):
    #     sock=self.getRandomSocket()
    #     rdata = []
    #     for t in data:
    #         rdata.append(t.encode())
    #     data = rdata
    #     databyte = MySend(datatype, data)
    #     result = bytearray(1)
    #     result[0]=255
    #     sock.sendto(result, self.ServerInfoAddr)
    #     if (getattr(sock, '_closed') == False):
    #         self.s.sendto(databyte, self.ServerInfoAddr)
    #     else:
    #         self.LoginSignal.emit(['2'])
    #         print(22)
    #     sock.close()

    def StrReceive(self,datalist):
        result=[]
        for data in datalist:
            result.append(data.decode())
        return result
        
    def run(self): 
        while self._MyThread__running.isSet():
            self._MyThread__flag.wait()      # 为True时立即返回, 为False时阻塞直到内部的标识位为True后返回
            try:
                data, addr = self.s.recvfrom(self.buff)
            except:
                break
            datalist=MyReceive(data)
            datatype=datalist[0]
            del datalist[0]
            datalist=self.StrReceive(datalist)
            if datatype==DataType.login_s_to_c.value:
                self.LoginSignal.emit(datalist)
            elif datatype==DataType.meetingid_s_to_c.value:
                self.MeetidSignal.emit(datalist[0])
            elif datatype==DataType.meetinfo_s_to_c.value:   
                # print(type(datalist[0]))
                self.MeetInfoSignal.emit(datalist[0])
            elif datatype==DataType.add_member_s_to_c.value:
                self.AddMemberSignal.emit(datalist)  
            elif datatype== DataType.msg_s_to_c.value:
                self.MsgSignal.emit(datalist)  
            elif datatype==DataType.memberquit_s_to_c.value:
                self.QuitMeetSignal.emit(datalist[0])   
            elif datatype == DataType.endmeet_s_to_c.value:
                self.EndMeetSignal.emit()
            elif datatype== DataType.membercamera_s_to_c.value:
                self.MemberCameraSignal.emit(datalist)
            elif datatype== DataType.membermicrophone_s_to_c.value:
                self.MemberMicrophoneSignal.emit(datalist)
            elif datatype==DataType.register_s_to_c.value:
                self.RegisterSignal.emit(datalist)
            elif datatype==DataType.existMeeting_s_to_c.value:
                self.ExistMeetingSignal.emit(datalist)
            elif datatype==DataType.changename_s_to_c.value:
                self.ChangeNameSignal.emit(datalist)
            elif datatype==DataType.changepwd_s_to_c.value:
                self.ChangePwdSignal.emit(datalist)
            elif datatype == DataType.handuplist_s_to_c.value:
                self.HandUpListSignal.emit(datalist)
            elif datatype == DataType.allmute_s_to_c.value:
                self.AllMuteSignal.emit()
            elif datatype == DataType.unallmute_s_to_c.value:
                self.UnAllMuteSignal.emit()
        self.s.close()
    
    def stop(self):
        super().stop()
        self.s.close()

class PyRecord(QObject):
    MsgSignal=pyqtSignal(str)
    def __init__(self) -> None:
        super().__init__()    
        self.allow_record = True
        self.audio_mutex=threading.Lock()
        self.video_mutex=threading.Lock()
        pass

    def record_screen(self):
        im = ImageGrab.grab()
        path=self.video_path +".avi"
        video = cv2.VideoWriter(path,cv2.VideoWriter_fourcc(*"XVID"),10,im.size)
        
        self.video_mutex.acquire()
        while self.allow_record:
            im = ImageGrab.grab()
            im = cv2.cvtColor(array(im), cv2.COLOR_RGB2BGR)
            video.write(im)
        video.release()
        self.video_mutex.release()

    def record_audio(self):
        # 如无法正常录音 请启用计算机的"立体声混音"输入设备
        CHUNK = 1024
        FORMAT = pyaudio.paInt16
        CHANNELS = 2
        RATE = 11025
        p = pyaudio.PyAudio()
        i=self.get_device_index('立体声混音')
        stream = p.open(
            input_device_index=i,
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK,
        )
        wf = wave.open(self.audio_path +".wav", "wb")
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        
        self.audio_mutex.acquire() #获取锁
        while self.allow_record:
            data = stream.read(CHUNK)
            wf.writeframes(data)

        stream.stop_stream()
        stream.close()
        p.terminate()
        wf.close()
        self.audio_mutex.release()
    def compose_file(self):
        self.MsgSignal.emit('正在合并视频&音频文件···')
        audio = AudioFileClip(self.audio_path + ".wav")
        video = VideoFileClip(self.video_path + ".avi")
        ratio = audio.duration / video.duration
        video = video.fl_time(lambda t: t / ratio, apply_to=["video"]).set_end(audio.duration)
            
        
        video = video.set_audio(audio)
        # video = video.volumex(5)
        video.write_videofile(
            self.file_path + "_out.avi", codec="libx264", fps=10, logger=None
        )
        video.close()
        self.MsgSignal.emit('合并视频&音频文件成功！')

    def remove_temp_file(self):
        self.MsgSignal.emit('正在删除缓存文件！')
        os.remove(self.audio_path + ".wav")
        os.remove(self.video_path + ".avi")
        self.MsgSignal.emit('删除缓存文件成功！')


    def record_end(self):
        self.audio_mutex.acquire()
        self.video_mutex.acquire()
        while True:
            self.compose_file()
            self.remove_temp_file()
            break
        self.audio_mutex.release()
        self.video_mutex.release()


    def stop(self):
        self.MsgSignal.emit('正在停止录制！')
        self.allow_record = False
        # time.sleep(1)
        t=threading.Thread(target=self.record_end)
        t.start()
       
    def run(self):
        timestr=str(datetime. now())
        now=timestr[:19].replace(':', '_')
        self.audio_path=f'./record/{now}audiotmp'
        self.video_path=f'./record/{now}videotmp'
        self.file_path=f'./record/{now}'
        
        t = threading.Thread(target=self.record_screen)
        t1 = threading.Thread(target=self.record_audio)
        t.start()
        t1.start()
        self.MsgSignal.emit('开始录制！')

    def get_device_index(self,target):
        p = pyaudio.PyAudio()
        count=p.get_device_count()
        for i in range(count):
            devInfo = p.get_device_info_by_index(i)
            if devInfo['name'].find(target) >= 0 and devInfo['hostApi'] == 0:#改变hostApi的数值采用内/外录制的方法。可以通过增加函数输出设备名称等信息。
                return i
        return -1
