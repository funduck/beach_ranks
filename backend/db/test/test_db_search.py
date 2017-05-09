from datetime import datetime

import pytest

from db.db_manage import Manage
from db.db_search import Search
from model import Player, Rating, Game


@pytest.mark.asyncio
async def test_all():
    # create players
    team_won = []
    team_lost = []
    g = None
    try:
        for i in range(0, 4):
            p = Player(nick=f'NewPlayer{i}', phone=f'7916123456{i}')
            p.set_rating(Rating(value=1200 + i, accuracy=1))
            if i < 2:
                team_won.append(p)
            else:
                team_lost.append(p)

            await Manage.save_player(p)

        # game
        g = Game(date=datetime.now(), nicks_won=[p.nick for p in team_won], nicks_lost=[p.nick for p in team_lost],
                 score_won=15, score_lost=10)
        for p in team_won:
            g.set_rating_before(p.nick, p.get_rating())
            p.set_rating(Rating(value=p.get_rating().value + 100, accuracy=p.get_rating().accuracy))
            g.set_rating_after(p.nick, p.get_rating())
            await Manage.save_player(p)

        for p in team_lost:
            g.set_rating_before(p.nick, p.get_rating())
            p.set_rating(Rating(value=p.get_rating().value - 100, accuracy=p.get_rating().accuracy))
            g.set_rating_after(p.nick, p.get_rating())
            await Manage.save_player(p)

        await Manage.save_game(g)

        # find game
        res = await Search.games(player=team_lost[0])
        assert res[0].id == g.id

        # find games vs
        res = await Search.games(player=team_won[0], vs_players=[team_lost[0]])
        assert len(res) == 1
        assert res[0].id == g.id

        # not find games vs
        res = await Search.games(player=team_lost[0], vs_players=[team_lost[1]])
        assert len(res) == 0

        # find games with
        res = await Search.games(player=team_lost[1], with_players=[team_lost[0]])
        assert len(res) == 1
        assert res[0].id == g.id

        # not find games with
        res = await Search.games(player=team_lost[0], with_players=[team_won[1]])
        assert len(res) == 0

        # find games vs and with
        res = await Search.games(player=team_lost[0], vs_players=[team_won[0]], with_players=[team_lost[1]])
        assert len(res) == 1
        assert res[0].id == g.id

        # not find games vs
        res = await Search.games(player=team_lost[1], vs_players=[team_won[1]], with_players=[team_won[0]])
        assert len(res) == 0

        res = await Search.games(player=team_lost[0], vs_players=[team_lost[1]], with_players=[team_lost[1]])
        assert len(res) == 0

    finally:
        # clear
        await Manage.delete_game(g)
        for player in team_lost + team_won:
            await Manage.delete_player(player)
