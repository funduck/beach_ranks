import typing

from collections import namedtuple

AddNickRequest = namedtuple('AddNickRequest', ['nick', 'phone'])
ForgetNickRequest = namedtuple('ForgetNickRequest', ['nick'])
AddGameRequest = namedtuple('AddGameRequest', ['nicks_won', 'nicks_lost', 'score_won', 'score_lost'])
GamesRequest = namedtuple('GetGamesRequest', ['nick', 'with_nicks', 'vs_nicks', 'count', 'max_game_id'])
PlayerRequest = namedtuple('GetPlayerRequest', ['nick'])
PlayersRequest = namedtuple('GetPlayersRequest', ['nick_like'])
TopRequest = namedtuple('TopRequest', ['offset', 'count'])

LISTS_DELIMITER = ';'


def valid_request_from_dict(request_type, args: typing.Dict):
    if request_type is AddNickRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nick')

        phone = args.get('phone', None)
        if phone is not None:
            try:
                int(phone)
            except Exception as e:
                raise AttributeError(f'Invalid arguments for {request_type.__name__}: invalid phone {phone} ')

        return AddNickRequest(nick=args['nick'], phone=phone)

    if request_type is ForgetNickRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nick')

        return ForgetNickRequest(nick=args['nick'])

    if request_type is AddGameRequest:
        if 'nicks_lost' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nicks_lost')

        if 'nicks_won' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nicks_won')

        return AddGameRequest(nicks_won=args['nicks_won'].split(LISTS_DELIMITER),
                              nicks_lost=args['nicks_lost'].split(LISTS_DELIMITER),
                              score_won=args.get('score_won', 0),
                              score_lost=args.get('score_lost', 0))

    if request_type is GamesRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nick')

        with_nicks = args['with_nicks'].split(LISTS_DELIMITER) if 'with_nicks' in args else None
        vs_nicks = args['vs_nicks'].split(LISTS_DELIMITER) if 'vs_nicks' in args else None
        count = args['count'] if 'count' in args else 10
        max_game_id = args['max_game_id'] if 'max_game_id' in args else 0
        return GamesRequest(nick=args['nick'], with_nicks=with_nicks, vs_nicks=vs_nicks,
            count=count, max_game_id=max_game_id)

    if request_type is PlayerRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nick')

        return PlayerRequest(nick=args['nick'])

    if request_type is PlayersRequest:
        if 'nick_like' not in args:
            raise AttributeError(f'Invalid arguments for {request_type.__name__}: no nick_like')

        return PlayersRequest(nick_like=args['nick_like'])

    if request_type is TopRequest:
        return TopRequest(offset=args.get('offset', '0'), count=args.get('count', '20')) 

    raise AttributeError(f'Unknown request type: {request_type.__name__}')
