from datetime import datetime
from typing import List

from common import initLogger
from model import Game, Player, Rating

from db.db_search import Search
from .db import db


ratingSystem = 'trueskill'
logger = initLogger('DBManage')


class Manage:
    @staticmethod
    async def add_nick(nick, rating=None, phone=None, who='test'):
        if nick is None:
            logger.error('add_nick: nick is None')
            raise AttributeError('add_nick: nick is None')

        p = Player(nick=nick, phone=phone)
        await p.load()

        p.nick = nick
        if phone is not None:
            p.phone = phone

        if rating is not None:
            p.set_rating('trueskill', rating)

        await p.save(who)
        return p

    @staticmethod
    async def add_game(nicks_won, nicks_lost, new_ratings, score_won=0, score_lost=0, who='test'):
        won = []
        for nick in nicks_won:
            p = Player(nick=nick)
            await p.load()
            won.append(p)
        lost = []
        for nick in nicks_lost:
            p = Player(nick=nick)
            await p.load()
            lost.append(p)

        # TODO what if we save same game too soon?

        g = Game(date=datetime.now(), team_won=won, team_lost=lost, score_won=score_won, score_lost=score_lost)
        await g.save(who)
        for p in won:
            # TODO real rating
            await g.save_rating(p, ratingSystem, p.get_rating(ratingSystem), new_ratings[p.nick])

        for p in lost:
            # TODO real rating
            await g.save_rating(p, ratingSystem, p.get_rating(ratingSystem), new_ratings[p.nick])
        return g

    @staticmethod
    def sql_save_player(player: Player, who):
        # table Players is (player_id number, nick varchar, phone varchar)
        sql = 'select * from beach_ranks.save_player(%s, %s, %s, %s);'
        params = [player.id, player.nick, player.phone, who]

        return [sql, params]

    @staticmethod
    def sql_save_rating(player: Player, who):
        # table Ratings is (rating_id varchar, player_id number, rating_code varchar, value number, accuracy number)
        sql = ''
        params = []
        for r_code in player.rating:
            rating = player.rating[r_code]
            sql += 'select * from beach_ranks.save_rating(%s, %s, %s, %s, %s);'
            params.extend([player.id, r_code, rating.value, rating.accuracy, who])

        return [sql, params]

    @staticmethod
    def sql_save_game(game: Game, who):
        # table Games is (game_id number, date date, score_won number, score_lost number)
        return [
            'select * from beach_ranks.save_game(%s, %s, %s, %s, %s);',
            [game.id, game.date.isoformat(), game.score_won, game.score_lost, who]
        ]

    @staticmethod
    def sql_save_game_players(game: Game, players_won: List[Player], players_lost: List[Player], who):
        # table Game_players is (game_id integer, player_id integer, win boolean)
        sqls = ''
        params = []
        for p in players_won:
            sqls += 'select * from beach_ranks.save_game_player(%s, %s, %s, %s);'
            params.extend([game.id, p.id, True, who])

        for p in players_lost:
            sqls += 'select * from beach_ranks.save_game_player(%s, %s, %s, %s);'
            params.extend([game.id, p.id, False, who])

        return [sqls, params]

    @staticmethod
    def sql_save_game_rating(game: Game, player_id, rating_code, rating_before: Rating, rating_after: Rating, who):
        return [
            'select * from beach_ranks.save_game_rating(%s, %s, %s, %s, %s, %s, %s, %s);',
            [game.id, player_id, rating_code, rating_before.value, rating_after.value,
             rating_before.accuracy, rating_after.accuracy, who]
        ]

    @staticmethod
    def sql_delete_game(game: Game):
        return [
            'delete from beach_ranks.games where game_id = %s;'
            'delete from beach_ranks.game_players where game_id = %s;'
            'delete from beach_ranks.game_ratings where game_id = %s;', [game.id, game.id, game.id]
        ]

    @staticmethod
    def sql_delete_player(player: Player):
        return [
            'delete from beach_ranks.ratings where player_id in '
            '(select player_id from beach_ranks.players where player_id = %s or nick = %s);'
            'delete from beach_ranks.players where player_id = %s or nick = %s;',
            [player.id, player.nick, player.id, player.nick]
        ]

    @staticmethod
    async def save_player(player: Player, who='test'):
        res = await db.execute(Manage.sql_save_player(player, who))
        player.id = res[0][0]
        if len(player.rating) > 0:
            await db.execute(Manage.sql_save_rating(player, who))

    @staticmethod
    async def save_game(game: Game, who='test'):
        res = await db.execute(Manage.sql_save_game(game, who))
        game.id = res[0][0]

        players_won = [await Search.load_player_by_nick(nick) for nick in game.nicks_won]
        players_lost = [await Search.load_player_by_nick(nick) for nick in game.nicks_lost]

        await db.execute(Manage.sql_save_game_players(game, players_won, players_lost, who))
        for p in players_won + players_lost:
            await db.execute(Manage.sql_save_game_rating(
                game,
                p.id,
                ratingSystem,
                game.rating_before(p.nick),
                game.rating_after(p.nick),
                who
            ))

    @staticmethod
    async def delete_game(game: Game):
        if game is not None:
            await db.execute(Manage.sql_delete_game(game))
        else:
            logger.warn('delete_game() game is None')

    @staticmethod
    async def delete_player(player: Player):
        if player is not None:
            await db.execute(Manage.sql_delete_player(player))
        else:
            logger.warn('delete_player() player is None')
