import asyncio

async def hello_world():
    print('Hello')
    await asyncio.sleep(1)
    print('World')

async def inner_coroutine():
    return 'Inner'

async def outer_coroutine():
    result = await inner_coroutine()
    print(result + ' Outer')
    return result + ' Outer'

loop = asyncio.get_event_loop()
loop.run_until_complete(asyncio.wait([outer_coroutine(),outer_coroutine()]))
# 对于 outer_coroutine()，不再需要 run_until_complete() 直接调用即可获取结果