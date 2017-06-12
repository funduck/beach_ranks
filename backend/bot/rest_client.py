import requests
import json

from common import initLogger
from model import player_from_dict, game_from_dict


LISTS_DELIMITER = ';'
logger = initLogger('BotRestClient')


def check_response_is_error(response):
    if 'error' in response:
        logger.error(f'server response is error: {response}')
        return response, None
    else:
        return None, response['result']


def do_request(url, params, method):
    try:
        if method == 'GET':
            return json.loads(requests.get(url=url, params=params).text)
        if method == 'POST':
            return json.loads(requests.post(url=url, params=params).text)
    except Exception as e:
        logger.error(f'do_request {params} {method} error: {e}')
        return {'error': str(e), 'error_type': 'client'}


class RestClient():
    def __init__(self, host, port):
        self.url = f'http://{host}:{port}/'

    def get_player(self, player=None, nick=None):
        if player is not None:
            nick=player.nick
        response = do_request(
            url=f'{self.url}player',
            params={'nick': nick},
            method='GET'
        )
        error, response = check_response_is_error(response)
        if error is None:
            return None, player_from_dict(response)
        else:
            return error, None

    def get_players(self, nick_like):
        response = do_request(
            url=f'{self.url}players',
            params={'nick_like': nick_like},
            method='GET'
        )
        error, response = check_response_is_error(response)
        if error is None:
            return None, [player_from_dict(player) for player in response]
        else:
            return error, None

    def add_player(self, player=None, nick=None, phone=None, who='test'):
        if player is not None:
            nick=player.nick
            phone=player.phone
        response = do_request(
            url=f'{self.url}nick',
            params={'nick': nick, 'phone': phone},
            method='POST'
        )
        error, response = check_response_is_error(response)
        if error is None:
            return None, player_from_dict(response)
        else:
            return error, None

    def forget_player(self, player=None, nick=None, phone=None, who='test'):
        if player is not None:
            nick=player.nick
            phone=player.phone
        response = do_request(
            url=f'{self.url}forget',
            params={'nick': nick, 'phone': phone},
            method='POST'
        )
        error, response = check_response_is_error(response)
        if error is None:
            return None, player_from_dict(response)
        else:
            return error, None

    def add_game(self, game=None, nicks_won=[], nicks_lost=[], score_won=None, score_lost=None, who='test'):
        if game is not None:
            nicks_won=game.nicks_won
            nicks_lost=game.nicks_lost
            score_won=game.score_won
            score_lost=game.score_lost
        response = do_request(
            url=f'{self.url}game',
            params={
                'nicks_won': LISTS_DELIMITER.join(nicks_won),
                'nicks_lost': LISTS_DELIMITER.join(nicks_lost),
                'score_won': score_won, 'score_lost': score_lost
            },
            method='POST'
        )
        error, response = check_response_is_error(response)
        if error is None:
            return None, game_from_dict(response)
        else:
            return error, None

    def get_games(self, nick=None, with_nicks=[], vs_nicks=[]):
        response = do_request(
            url=f'{self.url}games',
            params={
                'nick': nick,
                'with_nicks': LISTS_DELIMITER.join(with_nicks),
                'vs_nicks': LISTS_DELIMITER.join(vs_nicks)
            },
            method='GET'
        )
        error, response = check_response_is_error(response)
        if error is None:
            return None, [game_from_dict(game) for game in response]
        else:
            return error, None
