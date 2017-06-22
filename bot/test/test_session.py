import logging

from common.model import Player

from common.logger import get_logger
from ..session import Session
from ..telegram_interaction import MessageIds, TelegramInMessage
from ..texts import Texts

l = get_logger('Bot')
l.setLevel(logging.DEBUG)

l = get_logger('BotSession')
l.setLevel(logging.DEBUG)

logger = get_logger('TelegramInteraction')
l.setLevel(logging.DEBUG)


defaultRating = {
    'trueskill': 25
}


class EmptyBackend():
    def add_game(self, game, who):
        return None, game

    def add_player(self, player, who):
        return None, player

    def get_player(self, nick=None, phone=None):
        if nick == 'exists':
            return None, Player(nick=nick, phone=phone, rating=defaultRating)
        else:
            return {'error': f'Player not found: {nick}', 'error_type': 'negative response'}, None

    def get_players(self, nick_like):
        if nick_like == 'several':
            return None, [
                Player(nick='several1', phone='732422322'),
                Player(nick='several2', phone='732422323'),
                Player(nick='several3', phone='732422324')
            ]

        return None, []


sample_message = TelegramInMessage(
    kind='message',
    command='not important',
    input='not important too',
    ids=MessageIds(
        user_id=1,
        inline_query_id=None,
        message_id=2,
        chat_id=3
    )
)


def inline_message(command, user_input):
    return TelegramInMessage(
        kind='inline_query',
        command=command,
        input=user_input,
        ids=MessageIds(
            user_id=1,
            inline_query_id=1,
            message_id=2,
            chat_id=3
        )
    )


def test_init():
    s = Session()


def test_send_contact_1_known_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='exists', phone='7823434'))
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_send_contact_1_unknown_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='notexists', phone='7823435'))
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_add_1_unknown_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('game', ''),
        ('', 'notexists'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_inline_search_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    s.process_command(command='game', user_input='', processing_message=sample_message)
    s.process_command(command='players', user_input='several', processing_message=inline_message('players', 'several'))


def test_add_1_known_and_1_unknown_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='exists', phone='7823434')),
        ('', 'unknown player'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_add_4_known_players_and_set_scores():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='exists', phone='7823431')),
        ('game_player_confirm', Player(nick='exists', phone='7823432')),
        ('game_player_confirm', Player(nick='exists', phone='7823433')),
        ('game_player_confirm', Player(nick='exists', phone='7823434')),
        ('', 'not a number'),
        ('', '14'),
        ('', '15'),
        ('', '-1'),
        ('', '14'),
        ('', '13')
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_add_1_unknown_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('nick', ''),
        ('', 'unknown player'),
        ('nick_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_add_1_known_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('nick', ''),
        ('', 'exists')
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)


def test_search_player():
    s = Session()
    s.start(backend=EmptyBackend(), text=Texts())

    for i in (
        ('players', ''),
        ('', 'exists')
    ):
        s.process_command(command=i[0], user_input=i[1], processing_message=sample_message)
