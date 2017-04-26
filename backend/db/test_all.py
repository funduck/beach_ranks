from db_model_player import Player
from db_model_game import Game
from db_search import Search
import pytest
import pytest_asyncio
from datetime import datetime

@pytest.mark.asyncio
async def test_all():
    # create players
    p = []
    for i in range(0, 4):
        p.append(Player(nick='NewPlayer'+str(i), phone='7916123456'+str(i)))
        p[i].set_rating("trueskill", [1200+i, 1])
        await p[i].save()

    # game
    g = Game(date=datetime.now(), team_won=[p[0].id, p[1].id], team_lost=[p[2].id, p[3].id], score_won=15, score_lost=10)
    await g.save()

    # ratings
    for i in range(0, 4):
        await g.save_rating(p[i].id, "trueskill", p[i].get_rating("trueskill"), [1205+2-i, 0.9])
        p[i].set_rating("trueskill", [1205+2-i, 0.9])
        await p[i].save()

    # find game
    res = await Search.games(player=p[2])
    assert res[0].id == g.id

    # clear
    await g.delete_completely()
    for i in range(0, 4):
        await p[i].delete_completely()