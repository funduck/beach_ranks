import asyncio
import aiopg
import psycopg2
import re

class DBException(Exception):
    pass

class DB(object):
    def __init__(self):
        self.dsn = 'dbname=beach_ranks user=beach_ranks password=beachranks host=127.0.0.1 port=5432'
        self.do_fetch_regexp = re.compile("^(SELECT|select)")

    async def connect(self):
        self.conn_pool = await aiopg.create_pool(self.dsn)

    # script is list: [sql, list_of_params]
    async def execute(self, script, show_statement=True):
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

                    # to call commit() or rollback() later returning 'conn'
                    return ret
                except psycopg2.ProgrammingError as e:
                    print("error on script", script, "\n", e)
                    raise DBException(str(e))
