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
            raise RuntimeError(f'Invalid arguments: {args}')

        return AddNickRequest(nick=args['nick'], phone=args.get('phone', None))

    if request_type is ForgetNickRequest:
        if 'nick' not in args:
            raise RuntimeError(f'Invalid arguments: {args}')

        return ForgetNickRequest(nick=args['nick'])

    if request_type is AddGameRequest:
        if 'l1' not in args or 'l2' not in args:
            raise RuntimeError(f'Invalid arguments: {args}')

        if 'w1' not in args or 'w2' not in args:
            raise RuntimeError(f'Invalid arguments: {args}')

        return AddGameRequest(nicks_won=[args['w1'], args['w2']],
                              nicks_lost=[args['l1'], args['l2']],
                              score_won=args.get('score_won', 0),
                              score_lost=args.get('score_lost', 0))

    if request_type is GamesRequest:
        if 'nick' not in args:
            raise RuntimeError(f'Invalid arguments: {args}')

        with_nicks = args['with_nicks'].split(LISTS_DELIMITER) if 'with_nicks' in args else None
        vs_nicks = args['vs_nicks'].split(LISTS_DELIMITER) if 'vs_nicks' in args else None
        return GamesRequest(nick=args['nick'], with_nicks=with_nicks, vs_nicks=vs_nicks)

    if request_type is PlayerRequest:
        if 'nick' not in args:
            raise RuntimeError(f'Invalid arguments: {args}')

        return PlayerRequest(nick=args['nick'])

    raise RuntimeError(f'Unknown request type: {request_type}')