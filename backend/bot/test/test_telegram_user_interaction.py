import pytest
from telegram_user_interaction import TelegramUserInteraction


def send_request(arg):
    p = urllib.parse.urlencode(arg['body'])
    print('\n', arg['method'], '\n', arg['body'])
    url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (arg['method'], p)
    return json.loads(urllib.request.urlopen(url).read())


def test_echo_messaging():
    tui = TelegramUserInteraction(perform_request=send_request)