import logging
import requests
import json
from model import player_from_dict

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

    def get_player(self, name=None, phone=None, name_like=None):
        response = do_request(
            url=f'{self.url}player',
            params={'nick': name},
            method='GET'
        )
        error = check_response_is_error(response)
        if error is None:
            return player_from_dict(response)
        else:
            return error
