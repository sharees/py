import logging
logging.basicConfig(level=logging.INFO,  # 设置全局日志级别
                    format='%(asctime)s %(levelname)s: %(message)s',#%(pathname)s %(filename)s %(lineno)d  %(funcName)s 
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',  # 如果提供filename，则日志会输出到指定文件
                    filemode='a'  # 文件打开模式，'w'为覆盖写入，'a'为追加写入
                   )


def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

logging.info(create_args_string(10))
logging.error('error')