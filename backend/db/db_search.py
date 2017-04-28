from .db import db
from .db_model_player import Player
from .db_model_game import Game

import asyncio

class Search(object):
    @staticmethod
    def sql_find_all_games(player_id, vs_players=[], with_players=[]):
        sql = 'select gp.game_id from beach_ranks.game_players gp'
        params = [player_id]
        if len(vs_players) > 0:
            sql = sql + ', beach_ranks.game_players vs'
        if len(with_players) > 0:
            sql = sql + ', beach_ranks.game_players w'
        sql = sql + ' where gp.player_id = %s'
        for i in vs_players:
            sql = sql + ' and gp.game_id = vs.game_id and gp.win != vs.win and vs.player_id = %s'
            params.append(i)
        for i in with_players:
            sql = sql + ' and gp.game_id = w.game_id and gp.win = w.win and w.player_id = %s'
            params.append(i)
        sql = sql + ' order by gp.game_id desc'
        return [sql, params]

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
    async def games(player=None, vs_players=[], with_players=[]):
        vs_players_ids = []
        with_players_ids = []
        for p in vs_players:
            vs_players_ids.append(p.id)
        for p in with_players:
            with_players_ids.append(p.id)

        res = await db.execute(Search.sql_find_all_games(
            player_id=player.id, 
            vs_players=vs_players_ids, 
            with_players=with_players_ids))

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
