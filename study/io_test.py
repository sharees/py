import os
import pickle
import json
import shutil
print(os.name)
print(os.path.abspath('.'))
print(os.path.join(os.path.abspath('.'),'subdir'))
dir = [x for x in os.listdir('.') if os.path.isdir(x)]
print(dir)
filelist = [x for x in os.listdir('.') if os.path.isfile(x) and os.path.splitext(x)[1] == '.py']
print(filelist)


d =dict(name='like',age=30)
# with open('dump.txt','wb') as f:
#     pickle.dump(d,f)
print(json.dumps(d))

print(shutil.copy('io.txt','inputoutput.txt'))

# with open('dump.txt','rb') as f:
#     print(pickle.load(f))

# print(os.environ)
# with open('io.txt','w+',encoding='utf-8') as f:
#     f.write('what')