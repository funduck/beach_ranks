import json

import requests
from common.model import player_from_dict, game_from_dict

from common.logger import init_logger

LISTS_DELIMITER = ';'
logger = init_logger('BotRestClient')


def do_request(url, params, method):
    try:
        logger.debug(f'request {method} {url} {params}')
        if method == 'GET':
            response = requests.get(url=url, params=params)
        if method == 'POST':
            response = requests.post(url=url, params=params)
        text = response.text
        status_code = response.status_code
        logger.debug(f'response {status_code} {text}')
        return status_code, json.loads(text)
    except Exception as e:
        logger.error(f'do_request {params} {method} error: {e}')
        return 400, {'error': str(e), 'error_type': 'client'}


class RestClient():
    def __init__(self, host, port):
        self.url = f'http://{host}:{port}/'

    def get_player(self, player=None, nick=None):
        if player is not None:
            nick=player.nick
        code, response = do_request(
            url=f'{self.url}player',
            params={'nick': nick},
            method='GET'
        )
        if code != 200:
            return response
        else:
            return None, player_from_dict(response)

    def get_players(self, nick_like):
        code, response = do_request(
            url=f'{self.url}players',
            params={'nick_like': nick_like},
            method='GET'
        )
        if code != 200:
            return response
        else:
            return None, [player_from_dict(player) for player in response]

    def add_player(self, player=None, nick=None, phone=None, who='test'):
        if player is not None:
            nick=player.nick
            phone=player.phone
        code, response = do_request(
            url=f'{self.url}nick',
            params={'nick': nick, 'phone': phone, 'who': who},
            method='POST'
        )
        if code != 200:
            return response
        else:
            return None, player_from_dict(response)

    def forget_player(self, player=None, nick=None, phone=None, who='test'):
        if player is not None:
            nick=player.nick
            phone=player.phone
        code, response = do_request(
            url=f'{self.url}forget',
            params={'nick': nick, 'phone': phone, 'who': who},
            method='POST'
        )
        if code != 200:
            return response
        else:
            return None, player_from_dict(response)

    def add_game(self, game=None, nicks_won=[], nicks_lost=[], score_won=None, score_lost=None, who='test'):
        if game is not None:
            nicks_won=game.nicks_won
            nicks_lost=game.nicks_lost
            score_won=game.score_won
            score_lost=game.score_lost
        code, response = do_request(
            url=f'{self.url}game',
            params={
                'nicks_won': LISTS_DELIMITER.join(nicks_won),
                'nicks_lost': LISTS_DELIMITER.join(nicks_lost),
                'score_won': score_won, 'score_lost': score_lost, 'who': who
            },
            method='POST'
        )
        if code != 200:
            return response
        else:
            return None, game_from_dict(response)

    def get_games(self, nick=None, with_nicks=[], vs_nicks=[]):
        code, response = do_request(
            url=f'{self.url}games',
            params={
                'nick': nick,
                'with_nicks': LISTS_DELIMITER.join(with_nicks),
                'vs_nicks': LISTS_DELIMITER.join(vs_nicks)
            },
            method='GET'
        )
        if code != 200:
            return response
        else:
            return None, [game_from_dict(game) for game in response]
