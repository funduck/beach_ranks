from db_model_player import Player
import pytest
import pytest_asyncio

@pytest.mark.asyncio
async def test_save_player_and_delete():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_true_skill(1200, 1)
    await p.save()
    await p.delete_completely()

@pytest.mark.asyncio
async def test_save_player_load_by_id():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_true_skill(1200, 1)
    await p.save()
    l = Player(id=p.id)
    await l.load()
    assert l.nick == p.nick
    await p.delete_completely()

@pytest.mark.asyncio
async def test_save_player_load_by_phone():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_true_skill(1200, 1)
    await p.save()
    l = Player(phone=p.phone)
    await l.load()
    assert l.nick == p.nick
    await p.delete_completely()