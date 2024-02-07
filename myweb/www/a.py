import a


mod = __import__('b', globals(), locals())
print(dir(mod))
# mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)