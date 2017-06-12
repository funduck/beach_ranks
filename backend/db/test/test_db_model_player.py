import pytest

from db.db_model_player import Player, Rating


ratingSystem = 'trueskill'


@pytest.mark.asyncio
async def test_save_player():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating(ratingSystem, Rating(value=1200, accuracy=1))
    await p.save()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_player_and_update():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating(ratingSystem, Rating(value=1200, accuracy=1))
    await p.save()
    p.set_rating(ratingSystem, Rating(value=1203, accuracy=0.1))
    await p.save()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_player_load_by_id():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating(ratingSystem, Rating(value=1200, accuracy=1))
    await p.save()
    l = Player(id=p.id)
    await l.load()
    assert l.nick == p.nick
    r1 = p.get_rating(ratingSystem)
    r2 = l.get_rating(ratingSystem)
    assert r1[0] == r2[0]
    assert r1[1] == r2[1]
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_player_load_by_phone():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating(ratingSystem, Rating(value=1200, accuracy=1))
    await p.save()
    l = Player(phone=p.phone)
    await l.load()
    print (l.id, l.rating)
    assert l.nick == p.nick
    assert l.rating[ratingSystem]["value"] == p.rating[ratingSystem]["value"]
    assert l.rating[ratingSystem]["accuracy"] == p.rating[ratingSystem]["accuracy"]
    await p.delete_completely()
