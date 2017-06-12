import logging

from common import getLogger
from bot.session import Session
from bot.rest_client import RestClient
from bot.texts import Texts

l = getLogger('DB')
l.setLevel(logging.ERROR)

l = getLogger('Bot')
l.setLevel(logging.ERROR)

l = getLogger('BotSession')
l.setLevel(logging.ERROR)

logger = getLogger('TelegramInteraction')
l.setLevel(logging.ERROR)

l = getLogger('WebServer')
l.setLevel(logging.ERROR)

s = Session()
s.start(backend=RestClient('localhost', 8080), text=Texts(locale='ru'))
