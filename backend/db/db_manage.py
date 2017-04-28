from .db import db
from .db_model_player import Player
from .db_model_game import Game

import asyncio
from datetime import datetime

class ManageException(Exception):
    pass

class Manage(object):
    @staticmethod
    def set_initial_rating(p):
        if not 'trueskill' in p.rating:
            p.rating['trueskill'] = {'value': 1200, 'accuracy': 0}

    @staticmethod
    async def add_nick(player=None, nick=None, phone='', who='test'):
        if nick is None:
            raise ManageException('add_nick: nick is None')

        if player is not None:
            player.nick = nick
            await player.save(who)
            return

        p = Player(nick=nick, phone=phone)
        await p.load()

        Manage.set_initial_rating(p)
        
        p.nick = nick
        if phone is not None:
            p.phone = phone
        await p.save(who)
        return p

    @staticmethod
    async def add_game(players_won=None, players_lost=None, nicks_won=None, nicks_lost=None, 
        score_won=0, score_lost=0, who='test'):
        won = None
        lost = None
        if players_won is not None and players_lost is not None:
            won = players_won
            lost = players_lost
        else:
            if nicks_won is not None and nicks_lost is not None:
                won = []
                for nick in nicks_won:
                    p = Player(nick=nick)
                    await p.load()
                    Manage.set_initial_rating(p)
                    if p.id is None:
                        await p.save(who)
                    won.append(p)
                lost = []
                for nick in nicks_lost:
                    p = Player(nick=nick)
                    await p.load()
                    Manage.set_initial_rating(p)
                    if p.id is None:
                        await p.save(who)
                    won.append(p)

        # TODO what if we save same game too soon?

        g = Game(date=datetime.now(), team_won=won, team_lost=lost, score_won=score_won, score_lost=score_lost)
        await g.save(who)
        for p in won:
            # TODO real rating
            new_rating = [1205, 1]
            await g.save_rating(p, "trueskill", p.get_rating("trueskill"), new_rating)

        for p in lost:
            # TODO real rating
            new_rating = [1195, 1]
            await g.save_rating(p, "trueskill", p.get_rating("trueskill"), new_rating)
        return g