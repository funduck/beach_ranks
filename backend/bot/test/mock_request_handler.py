import typing
import datetime
import json
from .requests import AddNickRequest, ForgetNickRequest, AddGameRequest, GamesRequest, PlayerRequest, from_dict
from model import Player, Game, player_from_dict, game_from_dict


def request_from_dict(request_type, args):
    request = from_dict(request_type, args)
    if not isinstance(request, request_type):
        raise AttributeError(f'request is not {request_type.__name__}')
    return request


class MockRequestHandler:
    def __init__(self):
        super().__init__()

    async def get_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_nick(self, args: typing.Dict):
        request = request_from_dict(AddNickRequest, args)
        if request.nick == 'new':
            return json.dumps(Player(nick='new', phone=request.phone).as_dict())
        else:
            raise RuntimeError(f'Player already exists: {request.nick}')

    async def post_forget(self, args: typing.Dict):
        request = request_from_dict(ForgetNickRequest, args)
        return f'/forget?{args}'

    async def post_game(self, args: typing.Dict):
        request = request_from_dict(AddGameRequest, args)
        args['ratings'] = None
        args['date'] = datetime.datetime.now().isoformat(timespec='seconds')
        return json.dumps(game_from_dict(args).as_dict())

    async def get_games(self, args: typing.Dict):
        request = request_from_dict(GamesRequest, args)
        return f'/list?{args}'

    async def get_player(self, args: typing.Dict):
        request = request_from_dict(PlayerRequest, args)
        if request.nick == 'exists':
            return json.dumps(Player(nick='exist').as_dict())
        else:
            raise RuntimeError(f'Player not found: {request.nick}')

    async def get_help(self, args: typing.Dict):
        return f'/help?{args}'
