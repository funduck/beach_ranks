import aiohttp
import pytest
import json

from web_server import WebServer
from web_server import RequestHandler
import multiprocessing as mp


@pytest.fixture(scope='module')
def server_credentials():
    host, port = 'localhost', 9999
    server = WebServer(RequestHandler(), host=host, port=port)
    server_process = mp.Process(target=server.run)
    server_process.start()
    yield (host, port)
    server_process.terminate()
    server_process.join()


async def send_http_get(host, port, resource='', params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{host}:{port}/{resource}', params=params) as resp:
            return await resp.text()


async def send_http_post(host, port, resource='', params=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{host}:{port}{resource}', params=params) as resp:
            return await resp.text()


@pytest.mark.asyncio
@pytest.mark.parametrize('resource,method,query', [
    ('/', 'get', None),
    ('/', 'get', {'int': 1, 'str': '1'}),
    ('/nick', 'post', {'value': 'k1nkreet'}),
    ('/forget', 'post', {'value': 'k1nkreet'}),
    ('/game', 'post', {'value': 'game'}),
    ('/list', 'get', None),
    ('/list', 'get', {'value': 'recent'}),
    ('/help', 'get', None),
    ('/help', 'get', {'value': 'commands'}),
])
async def test_resources(server_credentials, resource, method, query):
    send_method = {
        'get':  send_http_get,
        'post': send_http_post
    }
    host, port = server_credentials
    resp_resource, resp_query = await send_method[method](host, port, resource, query).split(':')
    assert resource == resp_resource
    assert query == json.loads(resp_query)



