import asyncio
from aiohttp import web
import logging

logging.basicConfig(level=logging.DEBUG,  # 设置全局日志级别
                    format='%(filename)s %(lineno)d  %(funcName)s %(asctime)s %(levelname)s: %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    filename='a.log',  # 如果提供filename，则日志会输出到指定文件
                    filemode='a',  # 文件打开模式，'w'为覆盖写入，'a'为追加写入
                    encoding='utf-8'
                   )
logging.info('init')
async def site(request):
    # 直接返回字符串
    logging.info('abc')
    return 'abc'

async def response_factory(app, handler):
    async def middleware_handler(request):
        # 调用原请求处理器并获取其返回值
        try:
            response_text = await handler(request)
            logging.info('rs')
            logging.info(response_text)
        except Exception as e:
            logging.error(e)
        # 检查返回类型并创建适当的 web.Response 实例
        if isinstance(response_text, str):
            # 如果是字符串，则假设我们想以文本形式返回
            response = web.Response(text=response_text)
            response.content_type = 'text/plain;charset=utf-8'
        else:
            raise TypeError(f"Unsupported response type: {type(response_text)}")

        return response

    return middleware_handler

# 初始化应用
app = web.Application()

# 添加中间件，将 response_factory 应用于所有路由处理器
app.middlewares.append(response_factory)

# 添加路由，并使用 site 函数作为处理器
app.router.add_get('/', site)

# 启动服务器
web.run_app(app)