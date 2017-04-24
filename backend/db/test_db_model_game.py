from db_model_player import Player
from db_model_game import Game
import pytest
import pytest_asyncio
from datetime import datetime

@pytest.mark.asyncio
async def test_save_game_and_delete():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_true_skill(1200, 1)
    await p.save()

    g = Game(date=datetime.now(), team_won=[p.id, p.id], team_lost=[p.id, p.id], score_won=15, score_lost=10)
    await g.save()

    await g.delete_completely()
    await p.delete_completely()

@pytest.mark.asyncio
async def test_save_game_and_change():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_true_skill(1200, 1)
    await p.save()

    g = Game(date=datetime.now(), team_won=[p.id, p.id], team_lost=[p.id, p.id], score_won=15, score_lost=10)
    await g.save()
    g.score_won = 20
    await g.save()

    await g.delete_completely()
    await p.delete_completely()

@pytest.mark.asyncio
async def test_save_game_and_load():
    p = Player(nick='NewPlayer', phone='79161234567')
    p.set_true_skill(1200, 1)
    await p.save()

    g = Game(date=datetime.now(), team_won=[p.id, p.id], team_lost=[p.id, p.id], score_won=15, score_lost=10)
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
    p.set_true_skill(1200, 1)
    await p.save()

    g = Game(date=datetime.now(), team_won=[p.id, p.id], team_lost=[p.id, p.id], score_won=15, score_lost=10)
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