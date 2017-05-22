import json
import pytest

from web_server.rest_request_handler import RestRequestHandler
from web_server.test.mock_manage import MockManage
from web_server.test.mock_search import MockSearch


@pytest.fixture()
def storage():
    players = {}
    games = []
    return MockSearch(players, games), MockManage(players, games)


@pytest.mark.asyncio
async def test_nick(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'test'})
    assert await search.load_player_by_nick('test') is not None


@pytest.mark.asyncio
async def test_get_player(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'test'})
    output = await handler.handle_player({'nick': 'test'})
    assert isinstance(output, str)
    with pytest.raises(RuntimeError):
        await handler.post_nick({})
    with pytest.raises(RuntimeError):
        await handler.post_nick({'nick': 'test'})


@pytest.mark.asyncio
async def test_forget(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'test'})
    assert await search.load_player_by_nick('test') is not None
    await handler.post_forget({'nick': 'test'})
    assert await search.load_player_by_nick('test') is None
    with pytest.raises(RuntimeError):
        await handler.post_forget({'nick': 'non-existed'})
    with pytest.raises(RuntimeError):
        await handler.post_forget({})


@pytest.mark.asyncio
async def test_post_game(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'player1'})
    await handler.post_nick({'nick': 'player2'})
    await handler.post_nick({'nick': 'player3'})
    await handler.post_nick({'nick': 'player4'})
    await handler.post_game({'w1': 'player1', 'w2': 'player2', 'l1': 'player3', 'l2': 'player4',
                             'score_won': '15', 'score_lost': '13'})
    games = await search.games(nick='player1')
    assert len(games) == 1
    response = await handler.handle_games({'nick': 'player1'})
    games = json.loads(response)
    assert len(games) == 1
    response = await handler.handle_games({'nick': 'player2'})
    games = json.loads(response)
    assert len(games) == 1
    response = await handler.handle_games({'nick': 'player3'})
    games = json.loads(response)
    assert len(games) == 1
    response = await handler.handle_games({'nick': 'player4'})
    games = json.loads(response)
    assert len(games) == 1


@pytest.mark.asyncio
async def test_get_games(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'player1'})
    await handler.post_nick({'nick': 'player2'})
    await handler.post_nick({'nick': 'player3'})
    await handler.post_nick({'nick': 'player4'})
    await handler.post_game({'w1': 'player1', 'w2': 'player2', 'l1': 'player3', 'l2': 'player4',
                             'score_won': '15', 'score_lost': '13'})
    with pytest.raises(RuntimeError):
        await handler.handle_games({})

    response = await handler.handle_games({'nick': 'player1', 'with_nicks': 'player2'})
    games = json.loads(response)
    assert len(games) == 1

    response = await handler.handle_games({'nick': 'player1', 'with_nicks': 'player3'})
    games = json.loads(response)
    assert len(games) == 0

    response = await handler.handle_games({'nick': 'player1', 'with_nicks': 'player4'})
    games = json.loads(response)
    assert len(games) == 0

    response = await handler.handle_games({'nick': 'player1', 'vs_nicks': 'player2'})
    games = json.loads(response)
    assert len(games) == 0

    response = await handler.handle_games({'nick': 'player1', 'vs_nicks': 'player3'})
    games = json.loads(response)
    assert len(games) == 1

    response = await handler.handle_games({'nick': 'player1', 'vs_nicks': 'player4'})
    games = json.loads(response)
    assert len(games) == 1

    response = await handler.handle_games({'nick': 'player1', 'vs_nicks': 'player3;player4'})
    games = json.loads(response)
    assert len(games) == 1










