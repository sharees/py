#!/usr/bin/env python3
# -*- coding: utf-8 -*-

__author__ = 'Who'

import asyncio,logging
from typing import Any
import aiomysql
# from app import db_pool

def logSql(sql,args=()):
    logging.info(f"SQL: {sql}; args: {str(args)}")

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

async def select(sql,args=None,size=None):
    logSql(sql,args)
    global db_pool
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(sql.replace('?','%s'),args or ())
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
        logging.info('rows returned :%s' % len(rs))
        return rs

async def execute(sql,args=None,autocommit = True):
    logSql(sql,args)
    global db_pool
    async with db_pool.acquire() as conn:
        if not autocommit:
            await conn.begin()
        try:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql.replace('?','%s'),args)
                affected = cur.rowcount
            if not autocommit:
                await conn.commit()
        except BaseException as e:
            if not autocommit:
                await conn.rollback()
            raise
        return affected

def create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)

class Field(object):
    def __init__(self,name,column_type,primary_key,default) -> None:
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default
    def __str__(self) -> str:
        return f'{self.__class__.__name__},{self.column_type},{self.name}'
    
class StringField(Field):
    def __init__(self, name=None, primary_key = False, default=None,ddl='varchar(255)') -> None:
        super().__init__(name, ddl, primary_key, default)

class BooleanField(Field):
    def __init__(self, name=None, default=False) -> None:
        super().__init__(name, 'boolean', False, default)

class IntegerField(Field):
    def __init__(self, name=None, primary_key=False, default=0) -> None:
        super().__init__(name, 'bigint', primary_key, default)

class FloatField(Field):
    def __init__(self, name=None, primary_key=None, default=0.0) -> None:
        super().__init__(name, 'real', primary_key, default)

class TextField(Field):
    def __init__(self, name=None, default=None) -> None:
        super().__init__(name, 'text', False, default)

class ModelMetaclass(type):
    def __new__(cls,name,bases,attrs):
        if name == 'Model':
            return type.__new__(cls,name,bases,attrs)
        tableName = attrs.get('__table__',None) or name
        logging.info(f'found model:{name} (table:{tableName})')
        mappings = dict()
        fields = []
        primaryKey = None
        for k,v in attrs.items():
            if isinstance(v,Field):
                logging.info(f'foud mapping:{k}==>{v}')
                mappings[k] = v
                if v.primary_key:
                    if primaryKey:
                        raise ValueError(f'Duplicate primary key for field: {k}')
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise ValueError("Primary key not found.")
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f:'`%s`' % f, fields))
        logging.info(escaped_fields)
        attrs['__mappings__'] = mappings
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey
        attrs['__fields__'] = fields
        attrs['__select__'] = f'select `{primaryKey}`,{", ".join(escaped_fields)} from `{tableName}`'
        attrs['__insert__'] = f'insert into `{tableName}` ({", ".join(escaped_fields)},`{primaryKey}`) values({create_args_string(len(escaped_fields)+1)})'
        attrs['__update__'] = f'update `{tableName}` set {", ".join(list(map(lambda f: "`%s`=?" % (mappings.get(f).name or f),fields)))} where {primaryKey} = ?'    
        # attrs['__update__'] = f'update `{tableName}` set {", ".join(list(map(lambda f: "%s=?" %  f,escaped_fields)))} where {primaryKey} = ?'    
        attrs['__delete__'] = f'delete from `{tableName}` where `{primaryKey}` = ?'
        return type.__new__(cls,name,bases,attrs)

class Model(dict,metaclass=ModelMetaclass):
    def __init__(self,**kw):
        super().__init__(**kw)
    
    def __getattr__(self,key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)
    
    def __setattr__(self, key: str, value: Any) -> None:
        self[key]=value
    
    def getValue(self,key):
        return getattr(self,key,None)
    
    def getValueOrDefault(self,key):
        value = getattr(self,key,None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.info(f'using default value for {key}:{str(value)}')
                setattr(self,key,value)
        return value

    @classmethod
    async def findAll(cls,where=None,args=None,**kw):
        'find objects by where clause'
        sql = [cls.__select__]
        if where:
            sql.append('where')
            sql.append(where)
        if args is None:
            args = []
        orderBy = kw.get('orderBy',None)
        if orderBy:
            sql.append('order by')
            sql.append(orderBy)
        limit  = kw.get('limit',None)
        if limit is not None:
            sql.append('limit')
            if isinstance(limit,int):
                sql.append('?')
                args.append(limit)
            elif isinstance(limit,tuple) and len(limit) == 2:
                sql.append('?,?')
                args.extend(limit)
            else:
                raise ValueError(f'Invalid limit value:{str(limit)}')
        rs = await select(' '.join(sql),args)
        return [cls(**r) for r in rs]
    
    @classmethod
    async def findNumber(cls,selectField,where=None,args=None):
        'find number by select and where'
        sql = ['select %s _num_ from `%s`' % (selectField,cls.__table__)]
        if where:
            sql.append('where')
            sql.append(where)
        rs = await select(' '.join(sql),args,1)
        if len(rs) == 0:
            return None
        return rs[0]['_num_']
    
    @classmethod
    async def find(cls,pk):
        'find object by primary key'
        rs = await select('%s where %s = ?' % (cls.__select__,cls.__primary_key__),[pk],1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])
    
    async def save(self):
        args = list(map(self.getValueOrDefault,self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        rows = await execute(self.__insert__,args)
        if rows!=1:
            logging.warn('field to insert record:affected rows:%s' % rows)
        return rows
    
    async def update(self):
        args = list(map(self.getValue,self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        rows = await execute(self.__update__,args)
        if rows !=1:
            logging.warn('field to update by primary key:affected rows:%s' % rows)
        return rows
    
    async def remove(self):
        args = [self.getValue(self.__primary_key__)]
        rows = await execute(self.__delete__,args)
        if rows!=1:
            logging.warn('field to remove by primary key:affected rows %s' % rows)
        return rows
    
