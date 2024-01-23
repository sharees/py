class ListMetaclass(type):
    def __new__(cls,name,bases,attrs):
        print(cls,name,bases);
        attrs['add'] = lambda self,value:self.append(value)
        return type.__new__(cls,name,bases,attrs)

class MyList(list,metaclass=ListMetaclass):
    pass

L = MyList()
print(L)
L.add(2)
print(L)