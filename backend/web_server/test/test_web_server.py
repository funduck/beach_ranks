import multiprocessing as mp
import time

import aiohttp
import pytest

from web_server import RequestHandler
from web_server import WebServer


@pytest.fixture(scope='module')
def server_credentials():
    host, port = 'localhost', 9999
    server = WebServer(RequestHandler(), host=host, port=port)
    server_process = mp.Process(target=server.run)
    server_process.start()
    time.sleep(1)
    yield (host, port)
    server_process.terminate()
    server_process.join()


async def send_http_get(host, port, resource='', params=None):
    async with aiohttp.ClientSession() as session:
        async with session.get(f'http://{host}:{port}{resource}', params=params) as resp:
            text = await resp.text()
            return text


async def send_http_post(host, port, resource='', params=None):
    async with aiohttp.ClientSession() as session:
        async with session.post(f'http://{host}:{port}{resource}', params=params) as resp:
            return await resp.text()


@pytest.mark.asyncio
@pytest.mark.parametrize('resource,query', [
    ('/', None),
    ('/', {'p1': '1', 'p2': 'str'}),
    ('/list', None),
    ('/list', {'value': 'recent'}),
    ('/help', None),
    ('/help', {'value': 'commands'}),
])
async def test_get_resources(server_credentials, resource, query):
    host, port = server_credentials
    response = await send_http_get(host, port, resource, query)
    resp_resource, resp_query = response.split('?')

    assert resource == resp_resource
    if query is not None:
        assert str(query) == resp_query
    else:
        assert '{}' == resp_query


@pytest.mark.asyncio
@pytest.mark.parametrize('resource,query', [
    ('/nick', {'value': 'k1nkreet'}),
    ('/forget', {'value': 'k1nkreet'}),
    ('/game', {'value': 'game'}),
])
async def test_post_resources(server_credentials, resource, query):
    host, port = server_credentials
    response = await send_http_post(host, port, resource, query)
    resp_resource, resp_query = response.split('?')

    assert resource == resp_resource
    if query is not None:
        assert str(query) == resp_query
    else:
        assert '{}' == resp_query

