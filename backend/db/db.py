import asyncio
import aiopg
import psycopg2
import re
import asyncio

class DBException(Exception):
    pass

class DB(object):
    def __init__(self):
        self.dsn = 'dbname=beach_ranks user=beach_ranks password=beachranks host=127.0.0.1 port=5432'
        self.do_fetch_regexp = re.compile("^(SELECT|select)")
        self.conn_pool = None
        
    async def connect(self):
        self.conn_pool = await aiopg.create_pool(self.dsn)
        self.event_loop_id = id(asyncio.get_event_loop())
        
    # script is list: [sql, list_of_params]
    async def execute(self, script, show_statement=True):
        if self.conn_pool is None or self.conn_pool.closed == True or self.event_loop_id != id(asyncio.get_event_loop()):
            await self.connect()
        
        async with self.conn_pool.acquire() as conn:
            async with conn.cursor() as cur:
                try:
                    if show_statement:
                        print('executing sql:', script[0], script[1], '\n')

                    await cur.execute(script[0], script[1])

                    ret = []
                    if self.do_fetch_regexp.match(script[0]):
                        async for row in cur:
                            ret.append(row)

                    return ret
                except psycopg2.ProgrammingError as e:
                    print("error on script", script, "\n", e)                    
                    raise DBException(str(e))

db = DB()