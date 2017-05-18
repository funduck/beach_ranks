import typing

from collections import namedtuple

AddNickRequest = namedtuple('AddNickRequest', ['nick', 'phone'])
ForgetNickRequest = namedtuple('ForgetNickRequest', ['nick'])
AddGameRequest = namedtuple('AddGameRequest', ['nicks_won', 'nicks_lost', 'score_won', 'score_lost'])
GamesRequest = namedtuple('GetListRequest', ['nick', 'with_nicks', 'vs_nicks'])
PlayerRequest = namedtuple('GetPlayerRequest', ['nick'])


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

        return GamesRequest(nick=args['nick'], with_nicks=args.get('with_nicks', None),
                            vs_nicks=args.get('vs_nicks', None))
