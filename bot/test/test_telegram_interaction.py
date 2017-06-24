import json
import logging
import re

from common.model import Player

from common.logger import get_logger
from ..telegram_interaction import TelegramInteraction, TelegramOutMessage
from ..elements import Button

get_logger('TelegramInteraction').setLevel(logging.ERROR)


bot_name = 'beachranks_bot'

message_command = {
    "update_id": 269774610,
    "message": {
        "message_id": 404,
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "chat": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin",
            "type": "private"
        },
        "date": 1494088617,
        "text": "/nick",
        "entities": [
            {
                "type": "bot_command",
                "offset": 0,
                "length": 5
            }
        ]
    }
}

message_text = {
    "update_id": 269774620,
    "message": {
        "message_id": 405,
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "chat": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin",
            "type": "private"
        },
        "date": 1494090071,
        "text": "yeba"
    }
}

message_contact = {
    "update_id": 269774634,
    "message": {
        "message_id": 413,
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "chat": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin",
            "type": "private"
        },
        "date": 1494093427,
        "forward_from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "forward_date": 1494070509,
        "contact": {
            "phone_number": "790001",
            "first_name": "Гриша"
        }
    }
}

message_command_with_text = {
    "update_id": 269774621,
    "message": {
        "message_id": 406,
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "chat": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin",
            "type": "private"
        },
        "date": 1494090148,
        "text": "/cmd bebe be",
        "entities": [
            {
                "type": "bot_command",
                "offset": 0,
                "length": 4
            }
        ]
    }
}

inline_query_text = {
    "update_id": 269774615,
    "inline_query": {
        "id": "649988365309738432",
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "query": "some raw text",
        "offset": ""
    }
}

inline_query_command_with_text = {
    "update_id": 269774615,
    "inline_query": {
        "id": "649988365309738432",
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "query": "/cmd some raw text",
        "offset": ""
    }
}

callback_query = {
    "update_id": 269774629,
    "callback_query": {
        "id": "649988363781976086",
        "from": {
            "id": 151337209,
            "first_name": "Oleg",
            "last_name": "Milekhin",
            "username": "Oleg_Milekhin"
        },
        "message": {
            "message_id": 202,
            "from": {
                "id": 299909888,
                "first_name": "beachranks",
                "username": "beachranks_bot"
            },
            "chat": {
                "id": -218278839,
                "title": "test beachranks group chat",
                "type": "group",
                "all_members_are_administrators": True
            },
            "date": 1493668311,
            "edit_date": 1493668322,
            "reply_to_message": {
                "message_id": 201,
                "from": {
                    "id": 151337209,
                    "first_name": "Oleg",
                    "last_name": "Milekhin",
                    "username": "Oleg_Milekhin"
                },
                "chat": {
                    "id": -218278839,
                    "title": "test beachranks group chat",
                    "type": "group",
                    "all_members_are_administrators": True
                },
                "date": 1493668309,
                "text": "/listgames@beachranks_bot",
                "entities": [
                    {
                        "type": "bot_command",
                        "offset": 0,
                        "length": 25
                    }
                ]
            },
            "text": "press button or die"
        },
        "chat_instance": "3732815056849474797",
        "data": "/cmd some text or any params"
    }
}


# just command
def test_parse_message_command():
    m = message_command

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['message']['from']['id']
    assert r.ids.message_id == m['message']['message_id']
    assert r.ids.inline_query_id is None
    assert r.ids.chat_id == m['message']['chat']['id']

    assert r.kind == 'message'
    assert r.command == m['message']['text'][1:]
    assert r.input is None


# just text
def test_parse_message_text():
    m = message_text

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['message']['from']['id']
    assert r.ids.message_id == m['message']['message_id']
    assert r.ids.inline_query_id is None
    assert r.ids.chat_id == m['message']['chat']['id']

    assert r.kind == 'message'
    assert r.command is None
    assert r.input == m['message']['text']


# contact
def test_parse_message_contact():
    m = message_contact

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['message']['from']['id']
    assert r.ids.message_id == m['message']['message_id']
    assert r.ids.inline_query_id is None
    assert r.ids.chat_id == m['message']['chat']['id']

    assert r.kind == 'message'
    assert r.command is None
    assert r.input.equal(
        Player(
            nick=m['message']['contact']['first_name'],
            phone=m['message']['contact']['phone_number']
        )
    )


# command with text
def test_parse_message_command_with_text():
    m = message_command_with_text

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['message']['from']['id']
    assert r.ids.message_id == m['message']['message_id']
    assert r.ids.inline_query_id is None
    assert r.ids.chat_id == m['message']['chat']['id']

    assert r.kind == 'message'
    assert r.command == re.search('(\/\w*) (.*)', m['message']['text']).group(1)[1:]
    assert r.input == re.search('(\/\w*) (.*)', m['message']['text']).group(2)


# inline text
def test_parse_inline_query_text():
    m = inline_query_text

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['inline_query']['from']['id']
    assert r.ids.message_id is None
    assert r.ids.inline_query_id == m['inline_query']['id']
    assert r.ids.chat_id is None

    assert r.kind == 'inline_query'
    assert r.command is None
    assert r.input == m['inline_query']['query']


# inline command with text
def test_parse_inline_query_command_with_text():
    m = inline_query_command_with_text

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['inline_query']['from']['id']
    assert r.ids.message_id is None
    assert r.ids.inline_query_id == m['inline_query']['id']
    assert r.ids.chat_id is None

    assert r.kind == 'inline_query'
    assert r.command == re.search('(\/\w*) (.*)', m['inline_query']['query']).group(1)[1:]
    assert r.input == re.search('(\/\w*) (.*)', m['inline_query']['query']).group(2)


# callback query with data like '/cmd some text after' should be treated like regular message
def test_parse_callback_query():
    m = callback_query

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)
    assert r.ids.user_id == m['callback_query']['from']['id']
    assert r.ids.message_id is None # because here it would be bot's message
    assert r.ids.inline_query_id is None
    assert r.ids.chat_id == m['callback_query']['message']['chat']['id']

    assert r.kind == 'callback_query'
    assert r.command == re.search('(\/\w*) (.*)', m['callback_query']['data']).group(1)[1:]
    assert r.input == re.search('(\/\w*) (.*)', m['callback_query']['data']).group(2)


# simple message reply to message
def test_show_message_as_repsonse_to_message():
    m = message_command

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)

    ti = TelegramInteraction()

    rsp = ti.show_message(as_reply=r.ids, message='owls are not what they seem')

    assert rsp == TelegramOutMessage(
        method='sendMessage',
        body={
            'text': 'owls are not what they seem',
            'parse_mode': 'markdown',
            'chat_id': r.ids.chat_id,
            'reply_to_message_id': r.ids.message_id
        }
    )


# message with buttons reply to message
def test_show_message_as_repsonse_to_message():
    m = message_command

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)

    ti = TelegramInteraction()

    rsp = ti.show_message(
        as_reply=r.ids,
        message='press some buttons',
        buttons=[
            Button(text='ok', switch_inline=None, callback='/ok with param'),
            Button(text='no', switch_inline=None, callback='/no'),
            Button(text='search', switch_inline='/player ', callback=None),
        ]
    )

    assert rsp == TelegramOutMessage(
        method='sendMessage',
        body={
            'text': 'press some buttons',
            'parse_mode': 'markdown',
            'chat_id': r.ids.chat_id,
            'reply_to_message_id': r.ids.message_id,
            'reply_markup': json.dumps({
                'inline_keyboard': [[
                    {'text': 'ok', 'callback_data': '/ok with param'},
                    {'text': 'no', 'callback_data': '/no'},
                    {'text': 'search', 'switch_inline_query_current_chat': '/player '}
                ]]
            })
        }
    )


# message with buttons reply to callback
def test_show_message_as_repsonse_to_callback():
    m = callback_query

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)

    ti = TelegramInteraction()

    rsp = ti.show_message(
        as_reply=r.ids,
        message='press some buttons',
        buttons=[
            Button(text='ok', switch_inline=None, callback='/ok with param'),
            Button(text='no', switch_inline=None, callback='/no'),
            Button(text='search', switch_inline='/player ', callback=None),
        ]
    )

    assert rsp == TelegramOutMessage(
        method='sendMessage',
        body={
            'text': 'press some buttons',
            'parse_mode': 'markdown',
            'chat_id': r.ids.chat_id,
            'reply_markup': json.dumps({
                'inline_keyboard': [[
                    {'text': 'ok', 'callback_data': '/ok with param'},
                    {'text': 'no', 'callback_data': '/no'},
                    {'text': 'search', 'switch_inline_query_current_chat': '/player '}
                ]]
            })
        }
    )


# show contact list
def test_show_contacts():
    m = inline_query_text

    r = TelegramInteraction.parse_message(message=m, bot_name=bot_name)

    ti = TelegramInteraction()

    rsp = ti.show_contacts(
        as_reply=r.ids,
        contacts=[
            Player(nick='Jonny', phone='7123433'),
            Player(nick='B', phone='7123431'),
            Player(nick='Goode', phone='7123438')
        ]
    )

    assert rsp == TelegramOutMessage(
        method='answerInlineQuery',
        body={
            'inline_query_id': r.ids.inline_query_id,
            'results': json.dumps([{
                'type': 'contact',
                'id': '0',
                'phone_number': '7123433',
                'first_name': 'Jonny'
            },{
                'type': 'contact',
                'id': '1',
                'phone_number': '7123431',
                'first_name': 'B'
            },{
                'type': 'contact',
                'id': '2',
                'phone_number': '7123438',
                'first_name': 'Goode'
            }])
        }
    )
