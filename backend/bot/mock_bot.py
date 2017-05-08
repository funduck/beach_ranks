import pytest
import logging
import urllib.request
import json
import time

from model import Player
from bot.session import Session
from bot.common import ifNone
from bot.telegram_interaction import MessageIds, TelegramInMessage, TelegramOutMessage


def send_request(message):
    if message is None:
        return
    p = urllib.parse.urlencode(message.body)
    print('\n', message.method, '\n', message.body)
    url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (message.method, p)
    return json.loads(urllib.request.urlopen(url).read())


l = logging.getLogger('AbstractSession')
l.setLevel(logging.DEBUG)


class EmptyManage():
    def save_game(self, game, who):
        print(f'Game {game} saved by {who}')


class EmptySearch():
    def player(self, name=None, phone=None, name_like=None):
        if name == 'exists':
            return [Player(nick=name, phone=phone)]
        
        if name_like == 'several':
            return [
                Player(nick='several1', phone='732422322'),
                Player(nick='several2', phone='732422323'),
                Player(nick='several3', phone='732422324')
            ]
        
        return []


s = Session()
s.start(search=EmptySearch(), manage=EmptyManage())


def get_updates(last_id=0):
    updates = send_request(TelegramOutMessage(body={'offset': last_id+1}, method='getUpdates'))
    updates = updates['result']
    new_last_id = last_id
    for update in updates:
        print('\nresponding to:\n', update)

        if update['update_id'] > new_last_id:
            new_last_id = update['update_id']

        if last_id == 0:
            continue

        res = s.process_request(update)
        for response in res:
            send_request(response)

    return new_last_id


def run():    
    last_update = 0
    while True:
        last_update = get_updates(last_update)
        time.sleep(5)


run()