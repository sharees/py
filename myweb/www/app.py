import logging,aiomysql
import asyncio,os,json,time
from datetime import datetime
import sys
import traceback

from aiohttp import web
from jinja2 import Environment,FileSystemLoader
from coroweb import add_routes, add_static
from orm import Model,StringField,IntegerField,create_pool,execute,select

logging.basicConfig(level=logging.DEBUG,  # 设置全局日志级别
                    format='%(filename)s %(lineno)d  %(funcName)s %(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',  # 如果提供filename，则日志会输出到指定文件
                    filemode='a',  # 文件打开模式，'w'为覆盖写入，'a'为追加写入
                    encoding='utf-8'
                   )

#全局定義變量
db_pool = None

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

#初始化jinja2模板引擎
def init_jinja2(app,**kw):
    logging.info('init jinja2...')
    options = dict(
        autoescape = kw.get('autoescape', True),
        block_start_string = kw.get('block_start_string', '{%'),
        block_end_string = kw.get('block_end_string', '%}'),
        variable_start_string = kw.get('variable_start_string', '{{'),
        variable_end_string = kw.get('variable_end_string', '}}'),
        auto_reload = kw.get('auto_reload', True)
    )
    path = kw.get('path',None)
    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)),'templates')
    logging.info('set jinja2 template path:%s' % path)
    env = Environment(loader=FileSystemLoader(path),**options)
    filters = kw.get('filters',None)
    if filters is not None:
        for name,f in filters.items():
            env.filters[name] = f
    app['__temlating__'] = env

#日誌中間件
async def logger_factory(app,handler):
    async def logger(request):
        logging.info('Request:%s %s' % (request.method,request.path))
        return await handler(request)
    return logger

#數據處理中間件
async def data_factory(app,handler):
    async def parse_data(request):
        if request.method == 'POST':
            if request.content_type.startswith('application/json'):
                request.__data__ = await request.json()
                logging.info('request json :%s' % str(request.__data__))
            elif request.content_type.startswith('application/x-www-form-urlencoded'):
                request.__data__ = await request.post()
                logging.info('request form : %s' % str(request.__data__))
        return await handler(request)
    return parse_data

#响应中间件
async def response_factory(app,handler):
    async def response(request):
        logging.info('Resonse handler...')
        try:
            logging.info( handler)
            r = await handler(request)
        except Exception as e:
            exc_type, exc_value, exc_traceback = sys.exc_info()
            logging.error(f"Error occurred in handler: {str(e)}")
            logging.error("Traceback:")
            logging.error("\n".join(traceback.format_tb(exc_traceback)))
            return web.Response(status=500)
        logging.info('r:%s' % str(r))
        if isinstance(r,web.StreamResponse):
            return r
        if isinstance(r,bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octect-stream'
            return resp
        if isinstance(r,str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body = r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r,dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r,ensure_ascii=False,default=lambda o:o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r,int) and r >=100 and r < 600:
            return web.Response(r)
        if isinstance(r,tuple) and len(r) ==2:
            t,m = r
            if isinstance(t,int) and t>=100 and t<600:
                return web.Response(t,str(m))
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain;charset=utf-8'
        return resp
    return response

#
def datetime_filter(t):
    delta =int(time.time() - t)
    if delta < 60:
        return '1分钟前'
    if delta < 3600:
        return f'{delta//60}分钟前'
    if delta < 86400:
        return f'{delta//3600}小时前'
    if delta < 604800:
        return f'{delta//86400}天前'
    dt = datetime.fromtimestamp(t)
    return f'{dt.year}年{dt.month}月{dt.date}月'

#web框架初始化
async def init():
    global db_pool
    app = web.Application(middlewares=[logger_factory,response_factory])
    init_jinja2(app,filters=dict(datetime=datetime_filter))

    add_routes(app, 'handlers')
    add_static(app)

    # app.router.add_route('GET', '/', index)
    # app.router.add_route('GET', '/test', test)
    # app.router.add_route('GET', '/add', add)
    # app.router.add_route('GET', '/site', site)
    # app.router.add_route('GET', '/addsite', addSite)
    # app.router.add_route('GET', '/updateSite', updateSite)
    app.router.add_route('GET', '/delsite', delSite)
    db_pool =await create_pool(loop=asyncio.get_event_loop(), user='python', password='python', db="python")
    app['db_pool'] =db_pool
    return app

if __name__ == '__main__':
    app = init()
    web.run_app(app, host='127.0.0.1', port=9000)
 
