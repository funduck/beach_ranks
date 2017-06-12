import logging
import urllib.request
import json
import time

from common import getLogger
from bot.session import Session
from bot.telegram_interaction import TelegramInteraction, TelegramOutMessage
from bot.rest_client import RestClient
from bot.texts import Texts

l = getLogger('DB')
l.setLevel(logging.DEBUG)

l = getLogger('Bot')
l.setLevel(logging.DEBUG)

l = getLogger('BotSession')
l.setLevel(logging.DEBUG)

logger = getLogger('TelegramInteraction')
l.setLevel(logging.DEBUG)

l = getLogger('BotRestClient')
l.setLevel(logging.DEBUG)


def send_request(message):
    if message is None:
        return
    p = urllib.parse.urlencode(message.body)
    print('\n', message.method, '\n', message.body)
    url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (message.method, p)
    return json.loads(urllib.request.urlopen(url).read())


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
            s = Session()
            s.start(backend=RestClient('localhost', 8080), text=Texts(locale='ru'))
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
