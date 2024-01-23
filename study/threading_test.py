import time,threading


local_school = threading.local()

def process_student():
    std = local_school.student
    print('Hello,%s (in %s)' % (std,threading.current_thread().name))

def process_thread(name):
    local_school.student = name
    process_student()

t1 = threading.Thread(target= process_thread,args=('lily',),name="a-trheaidng")
t2 = threading.Thread(target= process_thread, args=('rusy',),name = 'b-threading')
t1.start()
t2.start()

t1.join()
t2.join()


# balance = 0
# lock = threading.Lock()
# def change_it(n):
#     global balance
#     balance = balance + n
#     balance = balance - n

# def run_thread(n):
#     for i in range(10000000):
#         lock.acquire()
#         try:
#             change_it(n)
#         finally:
#             lock.release()
# t1 = threading.Thread(target=change_it,args=(5,))
# t2 = threading.Thread(target=change_it,args=(8,))
# t1.start()
# t2.start()
# t1.join()
# t2.join()
# print(balance)



#新線程
# def loop():
#     print('thread %s is runing ...' % threading.current_thread().name)
#     n = 0 
#     while n<5:
#         n=n+1
#         print('thread %s >>> %s' % (threading.current_thread().name,n))
#         time.sleep(1)
#     print ('thread %s is ended.' % threading.current_thread().name)

# print('主thread %s is running ...' % threading.current_thread().name)

# t = threading.Thread(target=loop,name='SonThread')
# t.start()
# t.join()
# print('主thread %s ended.' % threading.current_thread().name)