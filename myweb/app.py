import logging,aiomysql
import asyncio,os,json,time
from datetime import datetime
from aiohttp import web
from orm import Model,StringField,IntegerField,create_pool,execute,select

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
    app.router.add_route('GET', '/test', test)
    app.router.add_route('GET', '/add', add)
    app.router.add_route('GET', '/site', site)
    app.router.add_route('GET', '/addsite', addSite)
    app.router.add_route('GET', '/updateSite', updateSite)
    app.router.add_route('GET', '/delsite', delSite)
    db_pool =await create_pool(loop=asyncio.get_event_loop(), user='python', password='python', db="python")
    app['db_pool'] =db_pool
    return app

class Sites(Model):
    id = IntegerField(primary_key=True)
    name = StringField()
    url = StringField()

async def site(request):
    get_params = request.rel_url.query
    id = get_params.get('id')
    rs = await Sites.find(id);
    return web.Response(text=str(rs), content_type='text/html')

async def addSite(request):
    m = Sites()
    m.name = 'meizhu'
    m.url = 'https://www.meizhu.com'
    rs = await m.save()
    return web.Response(text=str(rs), content_type='text/html')

async def updateSite(request):
    m = Sites()
    m.id = 12
    m.name = 'meizhu'
    m.url = 'https://www.meizhu.com/12'
    rs = await m.update()
    return web.Response(text=str(rs), content_type='text/html')

async def delSite(request):
    get_params = request.rel_url.query
    id = get_params.get('id')
    m = Sites()
    m.id = id
    rs = await m.remove()
    return web.Response(text=str(rs), content_type='text/html')

async def test(request):
   return web.Response(text='<h1>test</h1>', content_type='text/html')



async def add(request):
    # 獲取get數據
    get_params = request.rel_url.query
    name = get_params.get('name')
    url = get_params.get('url')

    # 获取POST表单数据
    # post_data = await request.post()
    # param_value = post_data.get('param_name')

    # 如果Content-Type是application/json，则可以这样获取数据
    if 'content-type' in request.headers and request.headers['content-type'] == 'application/json':
        post_data = await request.json()
        # 获取名为'param_name'的对象属性或键值
        param_value = post_data.get('param_name')

    sql = 'INSERT INTO `python`.`sites` (`name`, `url`) VALUES (?,?)'
    args = (name,url)
    affected = await execute(sql,args)
    return web.Response(text=str(affected), content_type='text/html')
 
async def index(request):
    rows = await select("SELECT * FROM sites")
    html = "<h1>Index</h1>"
    for row in rows:
        html += f"<p>{row}</p>"
    return web.Response(text=html, content_type='text/html')
 

if __name__ == '__main__':
    app = init()
    web.run_app(app, host='127.0.0.1', port=9000)
 
