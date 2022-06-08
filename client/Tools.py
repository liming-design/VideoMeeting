import cv2
import pyDes, binascii
import base64
from Crypto.Cipher import AES
import configparser

class VideoConvert:
    def __init__(self) -> None:
        pass


    @classmethod
    def JpegCompress2(self,img,quality=50):# quality 取值范围：0~100，数值越小，压缩比越高，图片质量损失越严重
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        times = 0
        while True:
            _, encode_img = cv2.imencode('.jpg', img, encode_param)
            times += 1
            if len(encode_img) <= 65000: 
                times=0
                return encode_img
            if times==2:
                encode_param[1] =40
            if times >2 :
                encode_param[1] -= 1

    @classmethod    
    def JpegCompress(self,img,quality=50):# quality 取值范围：0~100，数值越小，压缩比越高，图片质量损失越严重
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), quality]
        times = 0
        while True:
            _, encode_img = cv2.imencode('.jpg', img, encode_param)
            times += 1
            if len(encode_img) <= 65000: 
                times=0
                return encode_img
            if times==2:
                encode_param[1] =6
            if times >2 :
                encode_param[1] -= 1

    @classmethod
    def PngCompress(self,img,quality=9):# quality 取值范围：0~9，数值越大，压缩比越高，图片质量损失越严重
        params = [cv2.IMWRITE_PNG_COMPRESSION, quality]
        _, encode_img = cv2.imencode('.png', img, params)
        return encode_img

    @classmethod
    def UnCompress(self,show):
        show = cv2.imdecode(show, cv2.IMREAD_COLOR)#把图片解析出来
        return show

class DES:
    # 初始化key
    def __init__(self):
        pass
    @classmethod
    def AES_Encrypt(self,data,key):
        vi = '0102030405060708'
        pad = lambda s: s + (16 - len(s)%16) * chr(16 - len(s)%16)
        data = pad(data)
        # 字符串补位
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
        encryptedbytes = cipher.encrypt(data.encode('utf8'))
        # 加密后得到的是bytes类型的数据
        encodestrs = base64.b64encode(encryptedbytes)
        # 使用Base64进行编码,返回byte字符串
        enctext = encodestrs.decode('utf8')
        # 对byte字符串按utf-8进行解码
        return enctext

    @classmethod
    def AES_Decrypt(self,data,key):
        vi = '0102030405060708'
        data = data.encode('utf8')
        encodebytes = base64.decodebytes(data)
        # 将加密数据转换位bytes类型数据
        cipher = AES.new(key.encode('utf8'), AES.MODE_CBC, vi.encode('utf8'))
        text_decrypted = cipher.decrypt(encodebytes)
        unpad = lambda s: s[0:-s[-1]]
        text_decrypted = unpad(text_decrypted)
        # 去补位
        text_decrypted = text_decrypted.decode('utf8')
        return text_decrypted
 
    @classmethod
    def des_encrypt(self,s,key):
        """
        DES 加密
        :param s: 原始字符串
        :return: 加密后字符串
        """
        secret_key = key
        k = pyDes.des(secret_key, pyDes.triple_des, pad=None, padmode=pyDes.PAD_PKCS5)
        en = k.encrypt(s.encode("utf8"), padmode=pyDes.PAD_PKCS5)
        return binascii.b2a_hex(en).decode()
    
    @classmethod
    def des_decrypt(self,s,key):
        """
        DES 解密
        :param s: 加密后的字符串，16进制
        :return:  解密后的字符串
        """
        secret_key = key
        k = pyDes.des(secret_key, pyDes.triple_des, pad=None, padmode=pyDes.PAD_PKCS5)
        de = k.decrypt(binascii.a2b_hex(s), padmode=pyDes.PAD_PKCS5)
        return de.decode()



class ConfigFile:
    def __init__(self) -> None:
        self.filepath='config.ini'
    @classmethod
    def readConfig(self,key1,key2):
        config = configparser.ConfigParser()
        config.read(self.filepath)
        return config[key1][key2]
    
    @classmethod
    def writeConfig(self,data,key1,key2):
        config = configparser.ConfigParser()
        config.read(self.filepath)
        config.set(key1, key2, data) 
        config.write(open("config.ini", "r+", encoding="utf-8"))