from datetime import datetime

import pytest

from db.db_model_game import Game
from db.db_model_player import Player, Rating


@pytest.mark.asyncio
async def test_save_game_and_delete():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", Rating(accuracy=1200, value=1))
    await p.save()

    g = Game(date=datetime.now(), team_won=[p, p], team_lost=[p, p], score_won=15, score_lost=10)
    await g.save()

    await g.delete_completely()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_game_and_auto_save_players():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", Rating(value=1200, accuracy=1))

    g = Game(date=datetime.now(), team_won=[p, p], team_lost=[p, p], score_won=15, score_lost=10)
    await g.save(save_players=True)

    await g.delete_completely()
    await p.delete_completely()

@pytest.mark.asyncio
async def test_save_game_and_change():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", Rating(value=1200, accuracy=1))
    await p.save()

    g = Game(date=datetime.now(), team_won=[p, p], team_lost=[p, p], score_won=15, score_lost=10)
    await g.save()
    g.score_won = 20
    await g.save()

    await g.delete_completely()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_game_and_load():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", Rating(value=1200, accuracy=1))
    await p.save()

    g = Game(date=datetime.now(), team_won=[p, p], team_lost=[p, p], score_won=15, score_lost=10)
    await g.save()

    g2 = Game(id=g.id)
    await g2.load()

    assert g2.score_lost == g.score_lost
    assert g2.score_won == g.score_won

    await g.delete_completely()
    await g2.delete_completely()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_game_change_load():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", Rating(value=1200, accuracy=1))
    await p.save()

    g = Game(date=datetime.now(), team_won=[p, p], team_lost=[p, p], score_won=15, score_lost=10)
    await g.save()
    g.score_won = 25
    await g.save()

    g2 = Game(id=g.id)
    await g2.load()

    assert g2.score_lost == g.score_lost
    assert g2.score_won == 25

    await g.delete_completely()
    await g2.delete_completely()
    await p.delete_completely()


@pytest.mark.asyncio
async def test_save_game_and_rating_changes():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_rating("trueskill", Rating(value=1200, accuracy=1))
    await p.save()

    g = Game(date=datetime.now(), team_won=[p, p], team_lost=[p, p], score_won=15, score_lost=10)
    await g.save()
    # same player, different way to get skill
    await g.save_rating(p, "trueskill", p.get_rating("trueskill"), Rating(value=1206, accuracy=0.86))

    p.set_rating("trueskill", Rating(value=1206, accuracy=0.86))
    await p.save()

    await g.delete_completely()
    await p.delete_completely()
