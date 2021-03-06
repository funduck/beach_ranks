import os
import json
import logging
import typing
import urllib.request
from optparse import OptionParser

from common import WebServer

from bot.rest_client import RestClient
from bot.session import Session
from bot.telegram_interaction import TelegramInteraction
from bot.texts import Texts

logger = logging.getLogger('Bot')
logging.getLogger('Bot').setLevel(logging.DEBUG)
logging.getLogger('BotSession').setLevel(logging.DEBUG)
logging.getLogger('TelegramInteraction').setLevel(logging.DEBUG)
logging.getLogger('BotRestClient').setLevel(logging.DEBUG)
logging.getLogger('WebServer').setLevel(logging.DEBUG)


def send_request(message):
    if message is None:
        return
    p = urllib.parse.urlencode(message.body)
    print('\n', message.method, '\n', message.body)
    url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (message.method, p)
    return json.loads(urllib.request.urlopen(url).read())


class BotRestRequestHandler:
    def __init__(self, restHost, restPort):
        self.restHost = restHost
        self.restPort = restPort
        self.sessions = {}
        self.telegram = TelegramInteraction()

    async def get_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_beachranks_bot(self, args: typing.Dict):
        logger.debug(f'post_beachranks_bot {args}')
        update = args['body']
        if update is None:
            return 'no body'

        update = json.loads(update.decode('utf-8'))
        print('\nresponding to:\n', update)

        m = self.telegram.parse_message(message=update, bot_name='beachranks_bot')
        if m.ids.user_id in self.sessions:
            s = self.sessions[m.ids.user_id]
        else:
            s = Session()
            s.start(backend=RestClient(self.restHost, self.restPort), text=Texts(locale='ru')) # '185.4.74.144'
            self.sessions[m.ids.user_id] = s

        res = s.process_request(update)
        for response in res:
            send_request(response)


parser = OptionParser()
parser.add_option('-H', '--host', dest='host', help='host for web-server (0.0.0.0 by default)')
parser.add_option('-P', '--port', dest='port', help='port for web-server (8443 by default)')
(options, args) = parser.parse_args()
host = options.host
port = int(options.port) if options.port is not None else 8443

path = os.path.dirname(os.path.abspath(__file__))
server = WebServer(BotRestRequestHandler('localhost', 9999),
    host=options.host, port=port,
    ssl_files=(f'{path}/../common/test/cert.pem', f'{path}/../common/test/pkey.pem'))
server.run()
