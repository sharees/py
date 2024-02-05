import logging,aiomysql
import asyncio,os,json,time
from datetime import datetime
from aiohttp import web
import orm

logging.basicConfig(level=logging.INFO,  # 设置全局日志级别
                    format='%(filename)s %(lineno)d  %(funcName)s %(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',  # 如果提供filename，则日志会输出到指定文件
                    filemode='a',  # 文件打开模式，'w'为覆盖写入，'a'为追加写入
                    encoding='utf-8'
                   )

#全局定義變量
db_pool = None
db_test = 'a'
async def init():
    global db_pool
    app = web.Application()
    app.router.add_route('GET', '/', index)
    db_pool =await orm.create_pool(loop=asyncio.get_event_loop(), user='python', password='python', db="python")
    return app


async def index(request):
    global db_pool
    global db_test
    time.sleep(2)
    logging.error(db_test)
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute("SELECT * FROM sites")
            rows = await cur.fetchall()
    
    html = "<h1>Index</h1>"
    for row in rows:
        html += f"<p>{row}</p>"
    
    return web.Response(text=html, content_type='text/html')
 

if __name__ == '__main__':
    app = init()
    web.run_app(app, host='127.0.0.1', port=9000)
 
