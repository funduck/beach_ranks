import json
import logging
import time
import urllib.request

from common.model import Player

from bot.session import Session
from bot.telegram_interaction import TelegramInteraction, TelegramOutMessage
from bot.texts import Texts


def send_request(message):
    if message is None:
        return
    p = urllib.parse.urlencode(message.body)
    print('\n', message.method, '\n', message.body)
    url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (message.method, p)
    return json.loads(urllib.request.urlopen(url).read())


l = logging.getLogger('AbstractSession')
l.setLevel(logging.DEBUG)


known_players = ['гриша', 'тоня', 'масик', 'олег']


class EmptyManage():
    def save_game(self, game, who):
        for p in game.nicks_lost:
            known_players.append(p)
        for p in game.nicks_won:
            known_players.append(p)
        print(f'Game {game} saved by {who}')


class EmptySearch():
    def player(self, name=None, phone=None, name_like=None):
        like = []
        for n in known_players:
            if name is not None and n == name:
                return [Player(nick=n, phone='79000000')]

            if name_like is not None and n.startswith(name_like):
                like.append(Player(nick=n, phone='79000000'))
        return like


telegram = TelegramInteraction()
sessions = {}

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

        m = telegram.parse_message(message=update, bot_name='beachranks_bot')
        if m.ids.user_id in sessions:
            s = sessions[m.ids.user_id]
        else:
            s = Session(search=EmptySearch(), manage=EmptyManage(), text=Texts(locale='ru'))
            sessions[m.ids.user_id] = s

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
