import logging
logging.basicConfig(level=logging.INFO)

import asyncio,os,json,time
from datetime import datetime

from aiohttp import web

def index(request):
    return web.Response(body=b'<h1>Index</h1>')

async def handle(request):
    return web.Response(text="Hello, World!")

app = web.Application()
app.router.add_get('/', handle)
app.router.add_post('/',index)

web.run_app(app)
