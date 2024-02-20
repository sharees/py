bvar = 'bvar'

def hello(a,b,c='def'):
    print(f'a={a},b={b},c={c}')
# hello(b=1,a=2,c=3)

def args_1(*args):
    print(args)
# args_1(1,2,3)
    
def args_2(f,c,*arg,**args):
    print(arg)
    print(args)
# args_2(1,2,3,4,a=5,b=6)

def args_3(a):
    print(a)
args_3(a=6)


