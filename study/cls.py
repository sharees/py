from types import MethodType
class Student(object):
    name = '默認值'
    __slots__ = ('_age','other') # 用tuple定义允许绑定的属性名称
    def __init__(self):
        self._age = None
    
    #定義屬性
    @property
    def age(self):
        return self._age

    #設置屬性值
    @age.setter
    def age(self,value):
        if not isinstance(value,int):
            raise ValueError('數據類型錯誤')
        if value < 0 or value > 100:
            raise ValueError('值範圍錯誤!')
        self._age = value

    def show(self):
        return self.__addr

    def __getattr__(self,attr):
        if attr == 'score':
            return 99

class Boy(Student):
    def show(self):
        return self.name

s = Student()
#動態綁定方法
# def setAge(self,age):
#     self.age = age
# s.setAge = MethodType(setAge,s)
# s.setAge(10)
s.age = 10

setattr(s,'age',1)
print(s.score)
 