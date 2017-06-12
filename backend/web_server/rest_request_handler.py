import typing
from datetime import datetime

from model import Player, Game

import web_server.requests as requests
from db.db_manage import Manage
from db.db_search import Search
from ranking.ranking import TrueSkillRanking
from web_server.requests import AddNickRequest, ForgetNickRequest, AddGameRequest, GamesRequest, PlayerRequest
from web_server.web_server import OK_STATUS


def request_from_dict(request_type, args):
    request = requests.from_dict(request_type, args)
    if not isinstance(request, request_type):
        raise AttributeError(f'request is not {request_type.__name__}')
    return request


class RestRequestHandler:
    ranking = TrueSkillRanking

    def __init__(self, search=None, manage=None):
        self._search = search if search is not None else Search()
        self._manage = manage if manage is not None else Manage()

    async def get_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_nick(self, args: typing.Dict):
        request = request_from_dict(AddNickRequest, args)

        if await self._search.load_player_by_nick(request.nick) is not None:
            raise RuntimeError(f'Player already exists: {request.nick}')

        p = Player(nick=request.nick, phone=request.phone)
        p.set_rating(self.ranking.initial_rating())
        await self._manage.save_player(p)
        return p.as_dict()

    async def post_forget(self, args: typing.Dict):
        request = request_from_dict(ForgetNickRequest, args)

        p = await self._search.load_player_by_nick(request.nick)
        if p is None:
            raise RuntimeError(f'Player not found {request.nick}')

        await self._manage.delete_player(p)
        return p.as_dict()

    async def post_game(self, args: typing.Dict):
        request = request_from_dict(AddGameRequest, args)

        players = []
        for nick in request.nicks_won + request.nicks_lost:
            player = await self._search.load_player_by_nick(nick)
            if player is None:
                raise RuntimeError(f'Player not found: {nick}')
            if player.get_rating() is None:
                raise RuntimeError(f'Player rating is not set')
            players.append(player)

        game = Game(nicks_won=request.nicks_won, nicks_lost=request.nicks_lost,
                    score_won=request.score_won, score_lost=request.score_lost, date=datetime.now())
        for player in players:
            game.set_rating_before(player.nick, player.get_rating())

        self.ranking.calculate(game)
        await self._manage.save_game(game)

        for player in players:
            player.set_rating(game.rating_after(player.nick))
            self._manage.save_player(player)

        return game.as_dict()

    async def get_games(self, args: typing.Dict):
        request = request_from_dict(GamesRequest, args)

        games = await self._search.games(request.nick, request.with_nicks, request.vs_nicks)
        return [game.as_dict() for game in games]

    async def get_player(self, args: typing.Dict):
        request = request_from_dict(PlayerRequest, args)

        player = await self._search.load_player_by_nick(request.nick)
        if player is None:
            raise RuntimeError(f'Player not found: {request.nick}')

        return player.as_dict()

    async def get_help(self, args: typing.Dict):
        return f'/help?{args}'
