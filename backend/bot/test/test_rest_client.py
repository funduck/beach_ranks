import pytest
import multiprocessing as mp
import time
from bot.rest_client import RestClient
from web_server import WebServer
from .mock_request_handler import MockRequestHandler


@pytest.yield_fixture(scope='module')
def server_credentials():
    host, port = 'localhost', 8080
    server = WebServer(MockRequestHandler(), host=host, port=port)
    server_process = mp.Process(target=server.run)
    server_process.start()
    time.sleep(1)
    yield (host, port)
    server_process.terminate()
    server_process.join()

def test_get_player_not_found(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.get_player(name='not exists')
    assert 'error' in response

def test_get_player_found(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.get_player(name='exists')
    assert type(response).__name__ == 'Player'
