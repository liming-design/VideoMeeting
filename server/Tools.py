import hashlib

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

