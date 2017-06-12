import typing

from collections import namedtuple

AddNickRequest = namedtuple('AddNickRequest', ['nick', 'phone'])
ForgetNickRequest = namedtuple('ForgetNickRequest', ['nick'])
AddGameRequest = namedtuple('AddGameRequest', ['nicks_won', 'nicks_lost', 'score_won', 'score_lost'])
GamesRequest = namedtuple('GetListRequest', ['nick', 'with_nicks', 'vs_nicks'])
PlayerRequest = namedtuple('GetPlayerRequest', ['nick'])

LISTS_DELIMITER = ';'


def from_dict(request_type, args: typing.Dict):
    if request_type is AddNickRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments: no nick')

        phone = args.get('phone', None)
        if phone is not None:
            try:
                int(phone)
            except Exception as e:
                raise AttributeError(f'Invalid arguments: invalid phone {phone} ')

        return AddNickRequest(nick=args['nick'], phone=phone)

    if request_type is ForgetNickRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments: no nick')

        return ForgetNickRequest(nick=args['nick'])

    if request_type is AddGameRequest:
        if 'nicks_lost' not in args:
            raise AttributeError(f'Invalid arguments: no nicks_lost')

        if 'nicks_won' not in args:
            raise AttributeError(f'Invalid arguments: no nicks_won')

        return AddGameRequest(nicks_won=args['nicks_won'].split(LISTS_DELIMITER),
                              nicks_lost=args['nicks_lost'].split(LISTS_DELIMITER),
                              score_won=args.get('score_won', 0),
                              score_lost=args.get('score_lost', 0))

    if request_type is GamesRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments: no nick')

        with_nicks = args['with_nicks'].split(LISTS_DELIMITER) if 'with_nicks' in args else None
        vs_nicks = args['vs_nicks'].split(LISTS_DELIMITER) if 'vs_nicks' in args else None
        return GamesRequest(nick=args['nick'], with_nicks=with_nicks, vs_nicks=vs_nicks)

    if request_type is PlayerRequest:
        if 'nick' not in args:
            raise AttributeError(f'Invalid arguments: no nick')

        return PlayerRequest(nick=args['nick'])

    raise AttributeError(f'Unknown request type: {request_type}')
