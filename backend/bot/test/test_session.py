import pytest
from bot.session import Session
from bot.common_types import Contact


def test_init():
    s = Session()

    
def test_add_1_known_player():
    s = Session()
    s.start()
    for i in (
        ('game', ''),
        ('game_player_confirm', Contact(name='known player', phone='7823434'))
    ):
        s.process_command(command=i[0], input=i[1])


def test_add_1_unknown_player():
    s = Session()
    s.start()
    for i in (
        ('game', ''),
        ('game_add_new_player', 'unknown player'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], input=i[1])


def test_add_1_known_and_1_unknown_player():
    s = Session()
    s.start()
    for i in (
        ('game', ''),
        ('game_player_confirm', 'known player'),
        ('game_add_new_player', 'unknown player'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], input=i[1])


