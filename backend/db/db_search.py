from db import db
from db_model_player import Player
from db_model_game import Game

import asyncio

class Search(object):
    @staticmethod
    def sql_find_all_games(player_id):
        return ['select game_id from beach_ranks.game_players '\
            'where player_id = %s', [player_id]
            ]

    @staticmethod
    async def player(nick=None, phone=None):
        p = Player(nick=nick, phone=phone)
        await p.load()
        return p

    @staticmethod
    async def games(player=None, nick=None, phone=None):
        if player is None:
            p = await Search.player(nick, phone)
        else:
            p = player

        res = await db.execute(Search.sql_find_all_games(p.id))
        games = []
        for r in res:
            games.append(Game(id=r[0]))

        return games