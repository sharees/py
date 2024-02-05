#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Who'

import asyncio,logging
import aiomysql
from app import db_pool,db_test

def log(sql,args=()):
    logging.info(f"SQL:{sql}")

# orm.py文件
async def create_pool(loop, **kw):
    # logging.info(global_var)
    global db_pool   
    try:
        logging.info('创建数据库连接池...')
        db_pool = await aiomysql.create_pool(
            host=kw.get('host', 'localhost'),
            port=kw.get('port', 3306),
            user=kw['user'],
            password=kw['password'],
            db=kw['db'],
            charset=kw.get('charset', 'utf8mb4'),
            autocommit=kw.get('autocommit', True),
            maxsize=kw.get('maxsize', 1),
            minsize=kw.get('minsize', 1),
            loop=loop)
    except:
        logging.error('数据库连接失败!')
        return None  # 创建失败时返回None
      
    logging.info('数据库连接池创建成功：{}'.format(db_pool))
    return db_pool


async def close_pool():
    global db_pool
    db_pool.close()
    await db_pool.wait_closed()

async def select(sql,args,size=None):
    log(sql,args)
    global db_pool
    async with db_pool.get() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?','%s'),args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned :%s' % len(rs))
        return rs