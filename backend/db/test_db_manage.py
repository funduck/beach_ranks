from datetime import datetime

import pytest

from .db_model_game import Game
from .db_model_player import Player
from .db_manage import Manage


@pytest.mark.asyncio
async def test_all():
    # create players
    players = []
    for i in range(0, 4):
        players.append(await Manage.add_nick(nick='NewPlayer'+str(i)))

    g = await Manage.add_game(players_won=[players[0], players[1]], players_lost=[players[2], players[3]], 
        score_won=23, score_lost=21)

    # clear
    await g.delete_completely()
    for p in g.team_won:
        await p.delete_completely()
    for p in g.team_lost:
        await p.delete_completely()