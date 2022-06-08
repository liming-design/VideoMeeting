import sqlite3

class MyDataBase(object):
    def __init__(self):
        self.DbPath=r'MyDb.db'
        self.con=None
    
    def Open(self):
        if self.con == None:
            self.con = sqlite3.connect(self.DbPath)
            self.con.execute('pragma foreign_keys=on')
    
    def Close(self):
        if self.con!=None:
            self.con.close()
            self.con=None

    def Exists(self,sqlstr,args):
        try:
            self.Open()
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sqlstr, args)
            row = cursor.fetchone()  # 提取查询结果
        except Exception as e:
            print(e.__str__())
        finally:
            cursor.close()
            self.Close()
            if row != None:
                return True
            return False

    def Execute(self,sqlstr,args=[]):
        # insert into User(UserId,UserName,Pwd,CodeRule) values(?,?,?,?)
        try:
            self.Open()           
            cursor = self.con.cursor()  # 创建游标          
            cursor.execute(sqlstr,args)
            self.con.commit()
            return True
        except Exception as e:
            print(e.__str__())
            return False
        finally:
            cursor.close()
            self.Close()
        pass    

    def SelectAll(self,sqlstr,args=[]):
        try:
            self.Open()
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sqlstr,args)
            rows = cursor.fetchall()  # 提取查询结果           
            return rows 
            

        except Exception as e:
            print(e.__str__())
        finally:
            cursor.close()
            self.Close()
    
    def SelectOne(self,sqlstr,args=[]):
        try:
            self.Open()
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sqlstr, args)
            row = cursor.fetchone()  # 提取查询结果
            return row
        except Exception as e:
            print(e.__str__())
        finally:
            cursor.close()
            self.Close()



    def QueryLogin(self,id,pwd):
        row=[]
        try:
            self.Open()
            sql="select * from User where UserId=? and Pwd=?"
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sql, (id,pwd))
            row = cursor.fetchone()  # 提取查询结果
        except Exception as e:
            print(e.__str__())
        finally:
            cursor.close()
            self.Close()
            if len(row)>0:
                return True
            return False

    def QueryAll(self):
        rows=[]
        try:
            self.Open()
            sql="select UserId,UserName from User"
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sql)
            rows = cursor.fetchall()  # 提取查询结果
        except Exception as e:
            print(e.__str__())
        finally:
            cursor.close()
            self.Close()
            return rows

    def QueryRule(self,id):
        row=""
        try:
            self.Open()
            sql="select CodeRule from User where UserId=?"
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sql, (id,))
            row = cursor.fetchone()  # 提取查询结果
        except Exception as e:
            print(e.__str__())
        finally:
            cursor.close()
            self.Close()
            return row[0]

    def UpdateRule(self,id,rule):
        try:
            self.Open()
            sql="update User  set CodeRule=?  where UserId=?"
            cursor = self.con.cursor()  # 创建游标
            cursor.execute(sql, (rule,id))
            self.con.commit()
            return True
        except Exception as e:
            print(e.__str__())
            return False
        finally:
            cursor.close()
            self.Close()

    def AddUser(self,UserInfo):
        # insert into User(UserId,UserName,Pwd,CodeRule) values(?,?,?,?)
        try:
            self.Open()
            sql="insert into User values(?,?,?,?)"
            cursor = self.con.cursor()  # 创建游标
            uId=UserInfo[0]
            uname=UserInfo[1]
            pwd=UserInfo[2]
            rule=UserInfo[3]
            cursor.execute(sql,(uId,uname,pwd,rule))
            self.con.commit()
            return True
        except Exception as e:
            print(e.__str__())
            return False
        finally:
            cursor.close()
            self.Close()
        pass    

# db=MyDataBase()

# print(db.Exists('select * from User where UserId=? and Pwd=?',args=[123,223]))

