import pytest
import multiprocessing as mp
import time
from model import Player, Game
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
    response = client.get_player(nick='not exists')
    assert 'error' in response

def test_get_player_found(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.get_player(nick='exists')
    assert type(response).__name__ == 'Player'

def test_get_player_found_2(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.get_player(Player(nick='exists'))
    assert type(response).__name__ == 'Player'

def test_add_player_exists(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.add_player(nick='exists', phone='87892343')
    assert 'error' in response

def test_add_player_inalid_phone(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.add_player(nick='new', phone='2362783h')
    assert 'error' in response

def test_add_player_ok(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.add_player(nick='new', phone='731231213')
    assert type(response).__name__ == 'Player'

def test_add_player_ok_2(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.add_player(player=Player(nick='new', phone='731231213'))
    assert type(response).__name__ == 'Player'

def test_forget_player(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.forget_player(player=Player(nick='new', phone='731231213'))
    assert type(response).__name__ == 'Player'

def test_add_game_ok(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.add_game(nicks_won=['p1', 'p2'], nicks_lost=['p3', 'p4'], score_won=15, score_lost=13)
    assert type(response).__name__ == 'Game'

def test_add_game_ok_2(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.add_game(game=Game(nicks_won=['p1', 'p2'], nicks_lost=['p3', 'p4'], score_won=15, score_lost=13))
    assert type(response).__name__ == 'Game'

def test_get_games(server_credentials):
    host, port = server_credentials
    client = RestClient('localhost', 8080)
    response = client.get_games(nick='p1', with_nicks=['p2'], vs_nicks=['p3'])
    assert type(response[0]).__name__ == 'Game'
