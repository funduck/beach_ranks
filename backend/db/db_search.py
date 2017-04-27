from db import db
from db_model_player import Player
from db_model_game import Game

import asyncio

class Search(object):
    @staticmethod
    def sql_find_all_games(player_id):
        return [
            'select game_id from beach_ranks.game_players '
            'where player_id = %s', [player_id]
        ]

    @staticmethod
    def sql_rating_change(game_id, player_id, rating_code):
        return [
            'select value_before, value_after, accuracy_before, accuracy_after '
            'from beach_ranks.game_ratings gr, beach_ranks.ratings r '
            'where r.rating_id = gr.rating_id and r.player_id = %s '
            'and rating_code = %s and game_id = %s',
            [player_id, rating_code, game_id]
        ]

    @staticmethod
    async def player(nick=None, phone=None):
        p = Player(nick=nick, phone=phone)
        await p.load()
        return p

    @staticmethod
    async def games(player=None, nick=None, phone=None):
        if player is None:
            p = await Search.player(nick=nick, phone=phone)
        else:
            p = player

        res = await db.execute(Search.sql_find_all_games(p.id))
        games = []
        for r in res:
            g = Game(id=r[0])
            games.append(g)
            await g.load()

        return games

    @staticmethod
    async def rating_change(game, player, rating_code):
        res = await db.execute(Search.sql_rating_change(game.id, player.id, rating_code))
        res = res[0]
        return {
            "before": [res[0], res[2]],
            "after": [res[1], res[3]]
        }
