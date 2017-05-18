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
    assert len(search.players) == 1
    assert 'test' in search.players
    pytest.raises(RuntimeError, handler.post_nick, {'nick': 'test'})
    pytest.raises(RuntimeError, handler.post_nick, {})


@pytest.mark.asyncio
async def test_get_player(storage):
    search, manage = storage
    handler = RestRequestHandler(search, manage)
    await handler.post_nick({'nick': 'test'})
    output = await handler.handle_player({'nick': 'test'})
    assert isinstance(output, str)
    pytest.raises(RuntimeError, handler.handle_player, {})
    pytest.raises(RuntimeError, handler.handle_player, {'nick': 'non-existed'})
