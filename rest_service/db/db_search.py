import datetime
from typing import List

from common.logger import init_logger
from common.model import Player, Rating, Game

from .db import db


logger = init_logger('DBSearch')
ratingSystem = 'trueskill'


class Search:
    @staticmethod
    def sql_find_all_games(player_id, vs_players, with_players):
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
    async def games(player: Player, vs_players: List[Player] = None, with_players: List[Player] = None):
        vs_players_ids = []
        with_players_ids = []
        if vs_players is not None:
            for p in vs_players:
                vs_players_ids.append(p.id)
        if with_players is not None:
            for p in with_players:
                with_players_ids.append(p.id)

        res = await db.execute(Search.sql_find_all_games(
            player_id=player.id,
            vs_players=vs_players_ids,
            with_players=with_players_ids))

        games = []
        for r in res:
            games.append(await Search.load_game_by_id(game_id=r[0]))

        logger.debug(f'games {games}')
        return games

    @staticmethod
    async def rating_change(game, player, rating_code):
        res = await db.execute(Search.sql_rating_change(game.id, player.id, rating_code))
        res = res[0]
        rating_change = {
            "before": [res[0], res[2]],
            "after": [res[1], res[3]]
        }
        logger.debug(f'rating_change {rating_change}')
        return rating_change

    @staticmethod
    def sql_ratings(player_id):
        return [
            'select r.rating_code, value, accuracy, descr from beach_ranks.ratings r, beach_ranks.ratings_defs d '
            'where player_id = %s and r.rating_code = d.rating_code',
            [player_id]
        ]

    @staticmethod
    def sql_load_player_by_nick(nick):
        return [
            'select player_id, nick, phone from beach_ranks.players where nick = %s',
            [nick.strip()]
        ]

    @staticmethod
    def sql_load_player_by_id(player_id):
        return [
            'select player_id, nick, phone from beach_ranks.players where player_id = %s',
            [player_id]
        ]

    @staticmethod
    def sql_load_players_nick_like(nick):
        return [
            'select player_id, nick, phone from beach_ranks.players where UPPER(nick) LIKE UPPER(%s)',
            [f'%{nick.strip()}%']
        ]

    @staticmethod
    def sql_load_game_by_id(game_id):
        return [
            'select to_char(date, \'yyyy-mm-dd hh24:mi:ss\'), score_won, score_lost '
            'from beach_ranks.games where game_id = %s',
            [game_id]
        ]

    @staticmethod
    def sql_load_game_players_by_id(game_id):
        return [
            'select player_id, win from beach_ranks.game_players where game_id = %s',
            [game_id]
        ]

    @staticmethod
    def sql_load_games_by_nicks(nick, nicks_won, nicks_lost, count, max_game_id):
        return [
            'select distinct game_id '
            'from beach_ranks.game_players g, beach_ranks.players p '
            'where g.player_id = p.player_id and UPPER(nick) = UPPER(%s) '
            'and (game_id < %s or 0 >= %s) '
            'limit %s',
            [nick, max_game_id, max_game_id, count]
        ]
        # TODO nicks_won nicks_lost

    @staticmethod
    def sql_load_top_players(offset, count):
        return [
                'select p.player_id, nick, phone, value, accuracy '
                '        from beach_ranks.players p join beach_ranks.ratings r on '
                '            p.player_id = r.player_id '
                '        order by value desc '
                '        offset %s limit %s ',
                [offset, count]
        ]

    @staticmethod
    async def load_player_by_nick(nick):
        res = await db.execute(Search.sql_load_player_by_nick(nick))
        if len(res) == 0:
            logger.debug('load_player_by_nick None')
            return None

        player_id, nick, phone = res[0]
        p = Player(player_id=player_id, nick=nick, phone=phone)

        res = await db.execute(Search.sql_ratings(player_id))
        if len(res) > 0:
            p.set_rating(Rating(value=res[0][1], accuracy=res[0][2]))

        logger.debug(f'load_player_by_nick {p}')
        return p

    @staticmethod
    async def load_player_by_id(player_id):
        res = await db.execute(Search.sql_load_player_by_id(player_id))
        if len(res) == 0:
            logger.debug('load_player_by_nick None')
            return None

        player_id, nick, phone = res[0]
        p = Player(player_id=player_id, nick=nick, phone=phone)

        res = await db.execute(Search.sql_ratings(player_id))
        if len(res) > 0:
            p.set_rating(Rating(value=res[0][1], accuracy=res[0][2]))

        logger.debug(f'load_player_by_id {p}')
        return p

    @staticmethod
    async def load_players_nick_like(nick):
        res = await db.execute(Search.sql_load_players_nick_like(nick))

        players = []
        for record in res:
            player_id, nick, phone = record
            p = Player(player_id=player_id, nick=nick, phone=phone)

            res = await db.execute(Search.sql_ratings(player_id))
            if len(res) > 0:
                p.set_rating(Rating(value=res[0][1], accuracy=res[0][2]))

            players.append(p)

        logger.debug(f'load_players_nick_like {players}')
        return players

    @staticmethod
    async def load_game_by_id(game_id):
        g = Game(game_id=game_id)
        res = await db.execute(Search.sql_load_game_by_id(game_id))
        if len(res) == 0:
            raise RuntimeError(f'Could not find game game_id({g.id})')

        res = res[0]
        g.date = datetime.datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S')
        g.score_won = res[1]
        g.score_lost = res[2]

        res = await db.execute(Search.sql_load_game_players_by_id(game_id))

        for record in res:
            won = record[1]
            p = await Search.load_player_by_id(player_id=record[0])
            if won:
                g.nicks_won.append(p.nick)
            else:
                g.nicks_lost.append(p.nick)

            res = await db.execute(Search.sql_rating_change(g.id, p.id, ratingSystem))
            if len(res) == 0:
                raise RuntimeError(f'Could not find rating change for game_id({g.id}), player_id({p.id})')

            g.set_rating_before(p.nick, Rating(value=res[0][0], accuracy=res[0][2]))
            g.set_rating_after(p.nick, Rating(value=res[0][1], accuracy=res[0][3]))

        logger.debug(f'load_game_by_id {g}')
        return g

    @staticmethod
    async def load_games_by_nicks(nick, nicks_won, nicks_lost, count=10, max_game_id=0):
        res = await db.execute(Search.sql_load_games_by_nicks(nick, nicks_won, nicks_lost, count, max_game_id))
        if len(res) == 0:
            raise RuntimeError(f'Could not find games by nicks {nick} {nicks_won} {nicks_lost} {count} {max_game_id}')

        games = []
        for record in res:
            g = await Search.load_game_by_id(record[0])
            games.append(g)

        logger.debug(f'load_games_by_nicks {nick} {nicks_won} {nicks_lost} {count} {max_game_id}')
        return games

    @staticmethod
    async def load_top_players(offset, count):
        res = await db.execute(Search.sql_load_top_players(offset, count))
        players = []
        for record in res:
            player_id, nick, phone, value, accuracy = record
            p = Player(player_id=player_id, nick=nick, phone=phone)
            p.set_rating(Rating(value, accuracy))
            players.append(p)

        return players


