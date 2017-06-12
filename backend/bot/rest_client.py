import logging
import requests
import json
from model import player_from_dict, game_from_dict


LISTS_DELIMITER = ';'


def check_response_is_error(response):
    if 'error' in response:
        logging.error(f'server response is error: {response}')
        return response
    else:
        return None


def do_request(url, params, method):
    try:
        if method == 'GET':
            return json.loads(requests.get(url=url, params=params).text)
        if method == 'POST':
            return json.loads(requests.post(url=url, params=params).text)
    except Exception as e:
        logging.error(f'do_request {params} {method} error: {e}')
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
        error = check_response_is_error(response)
        if error is None:
            return player_from_dict(response)
        else:
            return error

    def add_player(self, player=None, nick=None, phone=None):
        if player is not None:
            nick=player.nick
            phone=player.phone
        response = do_request(
            url=f'{self.url}nick',
            params={'nick': nick, 'phone': phone},
            method='POST'
        )
        error = check_response_is_error(response)
        if error is None:
            return player_from_dict(response)
        else:
            return error

    def add_game(self, game=None, nicks_won=None, nicks_lost=None, score_won=None, score_lost=None):
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
        error = check_response_is_error(response)
        if error is None:
            return game_from_dict(response)
        else:
            return error
