import asyncio
from aiohttp import web

# 定义处理HTTP请求的异步函数
async def handle(request):
    name = request.match_info.get('name', "Anonymous")
    text = f"Hello, {name}!"
    return web.Response(text=text)

# 设置路由规则
app = web.Application()
app.add_routes([web.get('/', handle),  # 处理根路径请求
                web.get('/{name}', handle)])  # 处理形如'/yourname'的请求

# 启动服务器
async def main():
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, 'localhost', 8080)  # 监听本地8080端口
    await site.start()

    print("Server is running on http://localhost:8080")
    await asyncio.Future()  # 保持程序运行直到被外部中断（例如：Ctrl+C）

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        loop.run_until_complete(app.shutdown())
        loop.run_until_complete(runner.cleanup())
        loop.close()