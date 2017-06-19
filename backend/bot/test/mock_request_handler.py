import typing
import datetime
import json
from valid_requests import AddNickRequest, ForgetNickRequest, AddGameRequest, GamesRequest, PlayerRequest, PlayersRequest, valid_request_from_dict
from model import Player, Game, player_from_dict, game_from_dict


class MockRequestHandler:
    def __init__(self):
        super().__init__()

    async def get_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_nick(self, args: typing.Dict):
        request = valid_request_from_dict(AddNickRequest, args)
        if request.nick == 'new':
            return Player(nick='new', phone=request.phone).as_dict()
        else:
            raise RuntimeError(f'Player already exists: {request.nick}')

    async def post_forget(self, args: typing.Dict):
        request = valid_request_from_dict(ForgetNickRequest, args)
        return Player(nick=request.nick).as_dict()

    async def post_game(self, args: typing.Dict):
        request = valid_request_from_dict(AddGameRequest, args)
        args['ratings'] = None
        args['date'] = datetime.datetime.now().isoformat(timespec='seconds')
        return game_from_dict(args).as_dict()

    async def get_games(self, args: typing.Dict):
        request = valid_request_from_dict(GamesRequest, args)
        return [Game(
            nicks_won=[request.nick, request.with_nicks[0]],
            nicks_lost=[request.vs_nicks[0], 'p9'],
            score_won=16,
            score_lost=14,
            date=datetime.datetime.now()
        ).as_dict()]

    async def get_player(self, args: typing.Dict):
        request = valid_request_from_dict(PlayerRequest, args)
        if request.nick == 'exists':
            return Player(nick='exist').as_dict()
        else:
            raise RuntimeError(f'Player not found: {request.nick}')

    async def get_players(self, args: typing.Dict):
        request = valid_request_from_dict(PlayersRequest, args)
        if request.nick_like == 'exists':
            return [Player(nick='exist').as_dict()]
        else:
            return []

    async def get_help(self, args: typing.Dict):
        return f'/help?{args}'
