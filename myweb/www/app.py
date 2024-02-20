import logging
logging.basicConfig(level=logging.DEBUG,  # 设置全局日志级别
                    format='%(filename)s %(lineno)d  %(funcName)s %(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='app.log',  # 如果提供filename，则日志会输出到指定文件
                    filemode='a',  # 文件打开模式，'w'为覆盖写入，'a'为追加写入
                    encoding='utf-8'
                   )
import asyncio,os,json,time
from datetime import datetime
from aiohttp import web
from jinja2 import Environment,FileSystemLoader
from coroweb import add_routes, add_static
from orm import create_pool
from handlers import COOKIE_NAME,cookie2user
from config import configs



#全局定義變量
db_pool = None

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
    app['__templating__'] = env

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

async def auth_factory(app, handler):
    async def auth(request):
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(COOKIE_NAME)
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user.email)
                request.__user__ = user
        if request.path.startswith('/manage/') and (request.__user__ is None or not request.__user__.admin):
            return web.HTTPFound('/signin')
        return await handler(request)
    return auth

#响应中间件
async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        if isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        if isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        if isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False, default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json;charset=utf-8'
                return resp
            else:
                if request.__user__:
                    r['__user__'] = request.__user__
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html;charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(t, str(m))
        # default:
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
    app = web.Application()
    app.middlewares.append(logger_factory)
    app.middlewares.append(auth_factory)
    app.middlewares.append(response_factory)
    init_jinja2(app,filters=dict(datetime=datetime_filter))
    add_routes(app, 'handlers')
    add_static(app)
    db_pool =await create_pool(loop=asyncio.get_event_loop(), user=configs.db.user, password=configs.db.password, db=configs.db.db)
    app['db_pool'] =db_pool
    return app

if __name__ == '__main__':
    app = init()
    web.run_app(app, host='127.0.0.1', port=9000)
 
