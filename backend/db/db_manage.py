from datetime import datetime

from .db_model_player import Player
from .db_model_game import Game


class ManageException(Exception):
    pass


class Manage:
    @staticmethod
    async def add_nick(nick, rating=None, phone=None, who='test'):
        if nick is None:
            raise ManageException('add_nick: nick is None')

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
            await g.save_rating(p, "trueskill", p.get_rating("trueskill"), new_ratings[p.nick])

        for p in lost:
            # TODO real rating
            await g.save_rating(p, "trueskill", p.get_rating("trueskill"), new_ratings[p.nick])
        return g
