class Model(dict):
    def __init__(self, **kw):
        super().__init__(**kw)
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

class User(Model):
    pass

user = User(id=1, name=2, email=3, passwd=4, image=5)

print(user.id)