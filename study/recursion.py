import hello.pay
import sys
def log(func):
    def wrapper(*args,**kw):
        print('call%s():',func.__name__)
        return func(*args,**kw)
    return wrapper

@log
def now():
    print('now')

now()
hello.pay.log()
print(sys.path)