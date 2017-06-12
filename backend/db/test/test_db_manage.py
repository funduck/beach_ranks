from datetime import datetime
import logging

import pytest

from db.db_manage import Manage
from db.db_search import Search
from model import Player, Rating, Game


logging.getLogger('DB').setLevel(logging.ERROR)


@pytest.mark.asyncio
async def test_all():
    g = None
    team_won = []
    team_lost = []
    try:
        # create players
        for i in range(0, 4):
            p = Player(nick=f'NewPlayer{i}')
            p.set_rating(Rating(value=1200, accuracy=0))
            await Manage.delete_player(p)
            await Manage.save_player(p)
            if i < 2:
                team_won.append(p)
            else:
                team_lost.append(p)

        g = Game(date=datetime.now(), nicks_won=[p.nick for p in team_won], nicks_lost=[p.nick for p in team_lost], score_won=23, score_lost=21)
        for p in team_won:
            g.set_rating_before(p.nick, p.get_rating())
            p.set_rating(Rating(value=1300, accuracy=0))
            g.set_rating_after(p.nick, p.get_rating())

        for p in team_lost:
            g.set_rating_before(p.nick, p.get_rating())
            p.set_rating(Rating(value=1100, accuracy=0))
            g.set_rating_after(p.nick, p.get_rating())

        await Manage.save_game(g)

        test_g = await Search.load_game_by_id(g.id)

        assert test_g.nicks_won == ['NewPlayer0', 'NewPlayer1']
        assert test_g.nicks_lost == ['NewPlayer2', 'NewPlayer3']

        for nick in test_g.nicks_won:
            assert test_g.rating_before(nick) == Rating(value=1200, accuracy=0)
            assert test_g.rating_after(nick) == Rating(value=1300, accuracy=0)

        for nick in test_g.nicks_lost:
            assert test_g.rating_before(nick) == Rating(value=1200, accuracy=0)
            assert test_g.rating_after(nick) == Rating(value=1100, accuracy=0)

        assert test_g.score_won == 23
        assert test_g.score_lost == 21

    finally:
        # clear
        await Manage.delete_game(g)
        for p in team_won + team_lost:
            await Manage.delete_player(p)
