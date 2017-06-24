import pytest

from ..rest_request_handler import RestRequestHandler
from .mock_manage import MockManage
from .mock_search import MockSearch


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
    with pytest.raises(AttributeError):
        await handler.post_nick({})
    with pytest.raises(RuntimeError):
        await handler.post_nick({'nick': 'test'})


@pytest.mark.asyncio
async def test_get_player(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'test'})
    output = await handler.get_player({'nick': 'test'})
    assert isinstance(output, dict)
    with pytest.raises(RuntimeError):
        await handler.get_player({'nick': 'test_not_exists'})


@pytest.mark.asyncio
async def test_get_players(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'test'})
    output = await handler.get_players({'nick_like': 'test'})
    assert isinstance(output[0], dict)


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
    with pytest.raises(AttributeError):
        await handler.post_forget({})


@pytest.mark.asyncio
async def test_post_game(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'player1'})
    await handler.post_nick({'nick': 'player2'})
    await handler.post_nick({'nick': 'player3'})
    await handler.post_nick({'nick': 'player4'})
    await handler.post_game({'nicks_won': 'player1;player2', 'nicks_lost': 'player3;player4',
                             'score_won': '15', 'score_lost': '13'})
    games = await search.games(nick='player1')
    assert len(games) == 1
    response = await handler.get_games({'nick': 'player1'})
    games = response
    assert len(games) == 1
    response = await handler.get_games({'nick': 'player2'})
    games = response
    assert len(games) == 1
    response = await handler.get_games({'nick': 'player3'})
    games = response
    assert len(games) == 1
    response = await handler.get_games({'nick': 'player4'})
    games = response
    assert len(games) == 1


@pytest.mark.asyncio
async def test_get_games(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'player1'})
    await handler.post_nick({'nick': 'player2'})
    await handler.post_nick({'nick': 'player3'})
    await handler.post_nick({'nick': 'player4'})
    await handler.post_game({'nicks_won': 'player1;player2', 'nicks_lost': 'player3;player4',
                             'score_won': '15', 'score_lost': '13'})
    with pytest.raises(AttributeError):
        await handler.get_games({})

    response = await handler.get_games({'nick': 'player0'})
    games = response
    assert len(games) == 0

    response = await handler.get_games({'nick': 'player1', 'with_nicks': 'player2'})
    games = response
    assert len(games) == 1

    response = await handler.get_games({'nick': 'player1', 'with_nicks': 'player3'})
    games = response
    assert len(games) == 0

    response = await handler.get_games({'nick': 'player1', 'with_nicks': 'player4'})
    games = response
    assert len(games) == 0

    response = await handler.get_games({'nick': 'player1', 'vs_nicks': 'player2'})
    games = response
    assert len(games) == 0

    response = await handler.get_games({'nick': 'player1', 'vs_nicks': 'player3'})
    games = response
    assert len(games) == 1

    response = await handler.get_games({'nick': 'player1', 'vs_nicks': 'player4'})
    games = response
    assert len(games) == 1

    response = await handler.get_games({'nick': 'player1', 'vs_nicks': 'player3;player4'})
    games = response
    assert len(games) == 1
