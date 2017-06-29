from optparse import OptionParser
import json
import logging
import time
import urllib.request

from config.config import Config, initConfig

from bot.rest_client import RestClient
from bot.session import Session
from bot.telegram_interaction import TelegramInteraction, TelegramOutMessage
from bot.texts import Texts

logging.getLogger('Bot').setLevel(logging.DEBUG)
logging.getLogger('BotSession').setLevel(logging.DEBUG)
logging.getLogger('TelegramInteraction').setLevel(logging.DEBUG)
logging.getLogger('BotRestClient').setLevel(logging.DEBUG)


def send_request(message):
    if message is None:
        return
    p = urllib.parse.urlencode(message.body)
    # print('\n', message.method, '\n', message.body)
    url = f'https://api.telegram.org/{Config.bot.token}/%s?%s' % (message.method, p)
    return json.loads(urllib.request.urlopen(url).read())


telegram = TelegramInteraction()
sessions = {}


def get_updates(last_id=0):
    updates = send_request(TelegramOutMessage(body={'offset': last_id+1}, method='getUpdates'))
    updates = updates['result']
    new_last_id = last_id
    for update in updates:
        logging.getLogger('Bot').debug(f'responding to {update}')

        if update['update_id'] > new_last_id:
            new_last_id = update['update_id']

        if last_id == 0:
            continue

        m = telegram.parse_message(message=update, bot_name='beachranks_bot')
        if m.ids.user_id in sessions:
            s = sessions[m.ids.user_id]
        else:
            s = Session(
                backend=RestClient(Config.bot.host, Config.rest_service.port),
                text=Texts(locale=Config.bot.locale)
            ) # '185.4.74.144'
            sessions[m.ids.user_id] = s

        res = s.process_request(update)
        for response in res:
            send_request(response)

    return new_last_id


def run():
    last_update = 0
    while True:
        last_update = get_updates(last_update)
        time.sleep(2)


parser = OptionParser()
parser.add_option('-M', '--mode', dest='mode', help='mode for bot (can be test, by default is None, for unittest use unittest)')
(options, args) = parser.parse_args()

initConfig(options.mode)
run()
