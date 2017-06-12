import multiprocessing as mp
import time
import json

import pytest
import requests
from web_server import WebServer

from web_server.test.mock_request_handler import MockRequestHandler


@pytest.yield_fixture(scope='module')
def server_credentials():
    host, port = 'localhost', 9999
    server = WebServer(MockRequestHandler(), host=host, port=port)
    server_process = mp.Process(target=server.run)
    server_process.start()
    time.sleep(1)
    yield (host, port)
    server_process.terminate()
    server_process.join()


def send_http_get(host, port, resource='', params=None):
    r = requests.get(f'http://{host}:{port}{resource}', params=params)
    return json.loads(r.text)['result']


def send_http_post(host, port, resource='', params=None):
    r = requests.post(f'http://{host}:{port}{resource}', params=params)
    return json.loads(r.text)['result']


@pytest.mark.parametrize('resource,query', [
    ('/', None),
    ('/', {'p1': '1', 'p2': 'str'}),
    ('/list', None),
    ('/list', {'value': 'recent'}),
    ('/help', None),
    ('/help', {'value': 'commands'}),
])
def test_get_resources(server_credentials, resource, query):
    host, port = server_credentials
    response = send_http_get(host, port, resource, query)
    resp_resource, resp_query = response.split('?')

    assert resource == resp_resource
    if query is not None:
        assert str(query) == resp_query
    else:
        assert '{}' == resp_query


@pytest.mark.parametrize('resource,query', [
    ('/nick', {'value': 'k1nkreet'}),
    ('/forget', {'value': 'k1nkreet'}),
    ('/game', {'value': 'game'}),
])
def test_post_resources(server_credentials, resource, query):
    host, port = server_credentials
    response = send_http_post(host, port, resource, query)
    resp_resource, resp_query = response.split('?')

    assert resource == resp_resource
    if query is not None:
        assert str(query) == resp_query
    else:
        assert '{}' == resp_query
