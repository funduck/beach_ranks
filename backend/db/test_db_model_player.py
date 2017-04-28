import pytest

from .db_model_player import Player


@pytest.mark.asyncio
async def test_save_player():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", [1200, 1])
    await p.save()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_player_and_update():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", [1200, 1])
    await p.save()
    p.set_rating("trueskill", [1203, 0.1])
    await p.save()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_player_load_by_id():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", [1200, 1])
    await p.save()
    l = Player(id=p.id)
    await l.load()
    assert l.nick == p.nick
    r1 = p.get_rating("trueskill")
    r2 = l.get_rating("trueskill")
    assert r1[0] == r2[0]
    assert r1[1] == r2[1]
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_player_load_by_phone():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", [1200, 1])
    await p.save()
    l = Player(phone=p.phone)
    await l.load()
    print (l.id, l.rating)
    assert l.nick == p.nick
    assert l.rating["trueskill"]["value"] == p.rating["trueskill"]["value"]
    assert l.rating["trueskill"]["accuracy"] == p.rating["trueskill"]["accuracy"]
    await p.delete_completely()
