import subprocess
import time

import json
import os
import pytest
import requests
import logging

import sys


logging.getLogger('WebServer').setLevel(logging.ERROR)

cert_path = os.path.dirname(os.path.abspath(__file__))


@pytest.yield_fixture(scope='module')
def server_credentials():
    host, port = 'localhost', 9999
    path = os.path.dirname(os.path.abspath(__file__))
    env = os.environ.copy()
    p = subprocess.Popen([sys.executable, f'{path}/run_mock_ssl_web_server.py'], env=env)
    time.sleep(1)
    yield (host, port)
    p.kill()
    p.wait()


def send_https_get(host, port, resource='', params=None):
    r = requests.get(f'https://{host}:{port}{resource}', params=params, verify=False)
    return json.loads(r.text)['result']


def send_https_post(host, port, resource='', params=None):
    r = requests.post(f'https://{host}:{port}{resource}', params=params, verify=False)
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
