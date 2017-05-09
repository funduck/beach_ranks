import pytest
import logging
from model import Player
from bot.session import Session
from bot.common import ifNone
from bot.telegram_interaction import MessageIds, TelegramInMessage
from bot.texts import Texts


l = logging.getLogger('AbstractSession')
l.setLevel(logging.DEBUG)


class EmptyManage():
    def save_game(self, game, who):
        print(f'Game {game} saved by {who}')


class EmptySearch():
    def player(self, name=None, phone=None, name_like=None):
        if name == 'exists':
            return [Player(name, phone)]
        
        if name_like == 'several':
            return [
                Player('several1', '732422322'),
                Player('several2', '732422323'),
                Player('several3', '732422324')
            ]
        
        return []


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


def test_init():
    s = Session()

    
def test_send_contact_1_known_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage(), text=Texts())
    
    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='exists', phone='7823434'))
    ):
        s.process_command(command=i[0], input=i[1], processing_message=sample_message)


def test_send_contact_1_unknown_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage(), text=Texts())
    
    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='notexists', phone='7823435'))
    ):
        s.process_command(command=i[0], input=i[1], processing_message=sample_message)
        

def test_add_1_unknown_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage(), text=Texts())
    
    for i in (
        ('game', ''),
        ('', 'notexists'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], input=i[1], processing_message=sample_message)


def test_add_1_known_and_1_unknown_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage(), text=Texts())
    
    for i in (
        ('game', ''),
        ('game_player_confirm', Player(nick='exists', phone='7823434')),
        ('', 'unknown player'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], input=i[1], processing_message=sample_message)
        
def test_add_4_known_players_and_set_scores():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage(), text=Texts())
    
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
        s.process_command(command=i[0], input=i[1], processing_message=sample_message)