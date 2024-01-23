def f2(a, b, c=0, *args,**kw):
    print('a =', a, 'b =', b, 'c =', c,'args',args, 'kw =', kw)

args = (1, 2, 3, 4,5)
kw = {'d': 88, 'x': '#'}
f2(*args, **kw)