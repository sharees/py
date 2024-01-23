from types import MethodType
class Student(object):
    @property
    def age(self):
        return self._age
    @age.setter
    def age(self,value):
        if not isinstance(value,int):
            raise ValueError('數據類型錯誤')
        if value < 0 or value > 100:
            raise ValueError('值範圍錯誤!')
        self._age = value

    def show(self):
        return self.__addr


s = Student()
s.age = 10
print(s.age)
 