from datetime import datetime

import pytest

from db.db_model_game import Game
from db.db_model_player import Player
from db.db_search import Search


@pytest.mark.asyncio
async def test_all():
    # create players
    p = []
    for i in range(0, 4):
        p.append(Player(nick='NewPlayer'+str(i), phone='7916123456'+str(i)))
        p[i].set_rating("trueskill", [1200+i, 1])
        await p[i].save()

    # game
    g = Game(date=datetime.now(), team_won=[p[0], p[1]], team_lost=[p[2], p[3]], score_won=15, score_lost=10)
    await g.save()

    # ratings
    for i in range(0, 4):
        await g.save_rating(p[i], "trueskill", p[i].get_rating("trueskill"), [1205+2-i, 0.9])
        p[i].set_rating("trueskill", [1205+2-i, 0.9])
        await p[i].save()

    # find game
    res = await Search.games(player=p[2])
    assert res[0].id == g.id

    res = await Search.rating_change(g, p[0], "trueskill")
    assert res["before"][0] == 1200
    assert res["after"][0] == 1207

    # find games vs
    res = await Search.games(player=p[2], vs_players=[p[1]])
    assert res[0].id == g.id

    # not find games vs
    res = await Search.games(player=p[2], vs_players=[p[3]])
    assert len(res) == 0

    # find games with
    res = await Search.games(player=p[2], with_players=[p[3]])
    assert res[0].id == g.id

    # not find games with
    res = await Search.games(player=p[2], with_players=[p[0]])
    assert len(res) == 0

    # find games vs and with
    res = await Search.games(player=p[2], vs_players=[p[1]], with_players=[p[3]])
    assert res[0].id == g.id

    # not find games vs
    res = await Search.games(player=p[2], vs_players=[p[1]], with_players=[p[0]])
    assert len(res) == 0

    res = await Search.games(player=p[2], vs_players=[p[3]], with_players=[p[3]])
    assert len(res) == 0

    # clear
    await g.delete_completely()
    for i in range(0, 4):
        await p[i].delete_completely()