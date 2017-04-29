import pytest

from db.db_model_game import Game
from db.db_model_player import Rating, Player
from db.db_manage import Manage


@pytest.mark.asyncio
async def test_all():
    # create players
    players = []
    new_ratings = {}
    for i in range(0, 4):
        player = await Manage.add_nick(nick=f'NewPlayer{i}', rating=Rating(value=1200, accuracy=0))
        new_ratings[player.nick] = Rating(value=1300, accuracy=0)
        players.append(player)

    g = await Manage.add_game(nicks_won=[players[0].nick, players[1].nick],
                              nicks_lost=[players[2].nick, players[3].nick], new_ratings=new_ratings,
                              score_won=23, score_lost=21)

    test_g = Game(id=g.id)
    await test_g.load()

    assert [p.nick for p in test_g.team_won] == ['NewPlayer0', 'NewPlayer1']
    assert [p.nick for p in test_g.team_lost] == ['NewPlayer2', 'NewPlayer3']

    for p in test_g.team_won:
        assert p.get_rating('trueskill') == [1300, 0]

    assert test_g.score_won == 23
    assert test_g.score_lost == 21

    # clear
    await g.delete_completely()
    for p in g.team_won:
        await p.delete_completely()
    for p in g.team_lost:
        await p.delete_completely()
