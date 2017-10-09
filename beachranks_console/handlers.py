import requests


#beachranks_server = "http://185.4.74.144:9999"
beachranks_server = "http://localhost:9999"


def send_http_get(resourse, params=None):
    r = requests.get(f'{beachranks_server}{resourse}', params=params)
    return r.text


def send_http_post(resourse, params=None):
    r = requests.post(f'{beachranks_server}{resourse}', params=params)
    return r.text


def add_player(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    msg = send_http_post('/nick', {'nick': args[0]})
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def remove_player(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    msg = send_http_post('/forget', {'nick': args[0]})
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def player(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    msg = send_http_get('/player', {'nick': args[0]})
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def add_game(bot, update, args):
    if len(args) != 4:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected 4 player id)')

    msg = send_http_post('/game', {
        'nicks_won': f'{args[0]};{args[1]}',
        'nicks_lost': f'{args[2]};{args[3]}',
        'score_won': 0,
        'score_list': 0
        })
    bot.send_message(chat_ud=update.message.chat_id, text=msg)


def games(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    msg = send_http_get('/games', {'nick': args[0]})
    bot.send_message(chat_id=update.message.chat_id, text=msg)


def top(bot, update, args):
    number = 20
    if len(args) > 0 and args[0].isdigit():
        number = int(args[0])

    msg = send_http_get('/top', {'count': number})
    bot.send_message(chat_id=update.message.chat_id, text=msg)


