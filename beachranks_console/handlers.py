import requests
import json


beachranks_server = "http://localhost:9999"


def send_http_get(resourse, params=None):
    r = requests.get(f'{beachranks_server}{resourse}', params=params)
    if (r.status_code == 200)
        return json.loads(r.text)
    else:
        raise RuntimeError(r.text)


def send_http_post(resourse, params=None):
    r = requests.post(f'{beachranks_server}{resourse}', params=params)
    if (r.status_code == 200)
        return 'added'
    else:
        raise RuntimeError(r.text)


def players_response(response):
    output = ''
    index = 1
    for player in response:
        value = player['rating']['trueskill'][0]
        accuracy = player['rating']['trueskill'][1]
        output += f'{index}. {player["nick"]}: {value:.2f}, {accuracy:.2f}\n'
        index += 1
    return output


def games_response(response, player):
    output = ''
    index = 1
    for game in response:
        status = ''
        partner = ''
        enemy = []
        winners = game['nicks_won']
        losers = game['nicks_lost']

        if player in winners:
            status = 'won'
            for p in winners:
                if p != player:
                    partner = p
            enemy = losers
        else:
            status = 'lost'
            for p in losers:
                if p != player:
                    partner = p
            enemy = winners

        value_before = game['ratings'][player]['before']['trueskill'][0]
        acc_before = game['ratings'][player]['before']['trueskill'][1]
        value_after = game['ratings'][player]['after']['trueskill'][0]
        acc_after = game['ratings'][player]['after']['trueskill'][1]

        output += f'{index}. {status}. with: {partner}. vs: {enemy[0]}, {enemy[1]}, rating {value_before:.2f}, {acc_before:.2f} -> {value_after:.2f}, {acc_after:.2f}\n'

    return output


def add_player(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    try:
        msg = send_http_post('/nick', {'nick': args[0]})
        bot.send_message(chat_id=update.message.chat_id, text=players_response(msg))
    except RuntimeError as e:
        bot.send_message(chat_id=update.message.chat_id, text=f'failure: {e.message}')



def remove_player(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    try:
        msg = send_http_post('/forget', {'nick': args[0]})
        bot.send_message(chat_id=update.message.chat_id, text=msg)
    except RuntimeError as e:
        bot.send_message(chat_id=update.message.chat_id, text=f'failure: {e.message}')


def player(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    try:
        msg = send_http_get('/player', {'nick': args[0]})
        bot.send_message(chat_id=update.message.chat_id, text=players_response(msg))
    except RuntimeError as e:
        bot.send_message(chat_id=update.message.chat_id, text=f'failure: {e.message}')


def add_game(bot, update, args):
    if len(args) != 4:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected 4 player id)')

    try:
        msg = send_http_post('/game', {
            'nicks_won': f'{args[0]};{args[1]}',
            'nicks_lost': f'{args[2]};{args[3]}',
            'score_won': 0,
            'score_list': 0
            })
        bot.send_message(chat_ud=update.message.chat_id, text=msg)
    except RuntimeError as e:
        bot.send_message(chat_id=update.message.chat_id, text=f'failure: {e.message}')


def games(bot, update, args):
    if len(args) != 1:
        bot.send_message(chat_id=update.message.chat_id, text='Invalid parameters (expected player id)')

    try:
        msg = send_http_get('/games', {'nick': args[0]})
        bot.send_message(chat_id=update.message.chat_id, text=games_response(msg, args[0]))
    except RuntimeError as e:
        bot.send_message(chat_id=update.message.chat_id, text=f'failure: {e.message}')



def top(bot, update, args):
    number = 20
    if len(args) > 0 and args[0].isdigit():
        number = int(args[0])

    try:
        msg = send_http_get('/top', {'count': number})
        bot.send_message(chat_id=update.message.chat_id, text=players_response(msg))
    except RuntimeError as e:
        bot.send_message(chat_id=update.message.chat_id, text=f'failure: {e.message}')


