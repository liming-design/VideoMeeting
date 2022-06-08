import hashlib

data = "你好"   # 要进行加密的数据
data_sha = hashlib.sha256(data.encode('utf-8')).hexdigest()   
print(data_sha)

class HASH():
    def __init__(self) -> None:
        self.salt="iamcongzesheng"
        
    def HashSha256(self,string):
        sha256 = hashlib.sha256()
        sha256.update(string.encode('utf-8')+self.salt.encode('utf-8'))
        res = sha256.hexdigest()
        return res
    def Compare(self,string,hashvalue):
        ans=self.HashSha256(string)
        return hashvalue==ans


string = "qc/PhwG2kDMu4xH9M9l73Q=="
salt="iamcongzesheng"
sha256 = hashlib.sha256()
sha256.update(string.encode('utf-8')+salt.encode('utf-8'))
res = sha256.hexdigest()
print("sha256加密结果:",res)