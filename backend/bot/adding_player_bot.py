import urllib.request
import json
import time
from .telegram_user_interaction import TelegramUserInteraction
from .sc_adding_player import AddingPlayer
from .ui_types import PlayerContact


def send_request(arg):
    p = urllib.parse.urlencode(arg['body'])
    print('\n', arg['method'], '\n', arg['body'])
    url = 'https://api.telegram.org/bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8/%s?%s' % (arg['method'], p)
    return json.loads(urllib.request.urlopen(url).read())

    
class TestPlayerSearch():
    known = [
        PlayerContact(name='Серега (мопед)', phone='783249823'),
        PlayerContact(name='Вася (доктор)', phone='792623746'),
        PlayerContact(name='Масэ', phone='790223745')
    ]
    
    def like(self, input):
        if len(input) < 1:
            return []
        res = []
        for i in range(0, len(self.known)):
            if self.known[i].name.startswith(input):
                res.append(self.known[i])
        return res

tps = TestPlayerSearch()


def test_on_done(player):
    print('added player:', player)
    tps.known.append(player)


def run():
    tui = TelegramUserInteraction(send_request)
    adding = AddingPlayer(player_search=tps, user_interaction=tui, on_done=test_on_done)

    def get_updates(last_id=0):
        updates = send_request({
            'body': {'offset': last_id+1}, 
            'method': 'getUpdates'
        })
        updates = updates['result']
        new_last_id = last_id
        for update in updates:
            print('\nresponding to:\n', update)

            if update['update_id'] > new_last_id:
                new_last_id = update['update_id']

            if last_id == 0:
                continue

            tui.on_user_message(update)
        return new_last_id

        
    last_update = 0
    while True:
        last_update = get_updates(last_update)
        time.sleep(5)