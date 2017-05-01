import multiprocessing as mp
import ssl
import time

import aiohttp
import os
import pytest
import requests

from web_server import RequestHandler
from web_server import WebServer


cert_path = os.path.dirname(os.path.abspath(__file__))


@pytest.yield_fixture(scope='module')
def server_credentials():
    host, port = 'localhost', 9999
    server = WebServer(RequestHandler(), host=host, port=port,
                       ssl_files=(f'{cert_path}/cert.pem', f'{cert_path}/pkey.pem'))
    server_process = mp.Process(target=server.run)
    server_process.start()
    time.sleep(1)
    yield (host, port)
    server_process.terminate()
    server_process.join()


def send_https_get(host, port, resource='', params=None):
    r = requests.get(f'https://{host}:{port}{resource}', params=params, verify=False)
    return r.text


def send_https_post(host, port, resource='', params=None):
    r = requests.post(f'https://{host}:{port}{resource}', params=params, verify=False)
    return r.text


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
    response = send_https_get(host, port, resource, query)
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
    response = send_https_post(host, port, resource, query)
    resp_resource, resp_query = response.split('?')

    assert resource == resp_resource
    if query is not None:
        assert str(query) == resp_query
    else:
        assert '{}' == resp_query

