import typing
from datetime import datetime

from db.db_manage import Manage
from db.db_search import Search
import web_server.requests as requests
from model import Player, Game
from ranking.ranking import TrueSkillRanking
from web_server.requests import AddNickRequest, ForgetNickRequest, AddGameRequest, GetListRequest


class RestRequestHandler:
    ranking = TrueSkillRanking

    def __init__(self):
        pass

    async def handle_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_nick(self, args: typing.Dict):
        request = requests.from_dict(AddNickRequest, args)
        if not isinstance(request, AddNickRequest):
            raise RuntimeError('Parse error')

        if await Search.load_player_by_nick(request.nick) is not None:
            raise RuntimeError(f'Player already exists: {request.nick}')

        p = Player(nick=request.nick, phone=request.phone)
        p.set_rating(self.ranking.initial_rating())
        await Manage.save_player(p)

    async def post_forget(self, args: typing.Dict):
        request = requests.from_dict(ForgetNickRequest, args)
        if not isinstance(request, ForgetNickRequest):
            raise RuntimeError('Parse error')
        
        p = await Search.load_player_by_nick(request.nick)
        if p is None:
            raise RuntimeError(f'Player not found {request.nick}')
        
        await Manage.delete_player(p)

    async def post_game(self, args: typing.Dict):
        request = requests.from_dict(AddGameRequest, args)
        if not isinstance(request, AddGameRequest):
            raise RuntimeError('Parse error')

        players = []
        for nick in request.nicks_won + request.nicks_lost:
            player = await Search.load_player_by_nick(nick)
            if player is None:
                raise RuntimeError(f'Player not found: {nick}')
            players.append(player)

        game = Game(nicks_won=request.nicks_won, nicks_lost=request.nicks_lost,
                    score_won=request.score_won, score_lost=request.score_lost, date=datetime.now())
        self.ranking.calculate(game)
        await Manage.save_game(game)
        for player in players:
            player.set_rating(game.rating_after(player.nick))
            Manage.save_player(player)

    async def handle_list(self, args: typing.Dict):
        request = requests.from_dict(GetListRequest, args)
        if not isinstance(request, GetListRequest):
            raise RuntimeError(f'Parse error')

        games = await Search.games(request.nick, request.with_nick, request.vs_nick)
        return f'{games}'

    def handle_help(self, args: typing.Dict):
        return f'/help?{args}'
