import pytest
from bot.session import Session
from bot.common_types import Contact
from bot.common import ifNone


class EmptyPlayer():
    def __init__(self, name=None, phone=None):
        self.name = None
        self.phone = None
        
        
class EmptyGame():
    def __init__(self, id=None, date=None, team_won=None, team_lost=None, score_won=None, score_lost=None):
        self.id = id
        self.date = date
        self.team_won = ifNone(team_won, [])  # array of Players in team that won
        self.team_lost = ifNone(team_lost, [])  # array of Players in team that lost
        self.score_won = score_won
        self.score_lost = score_lost

        
class EmptyManage():
    def new_game(self):
        return EmptyGame()
        
    def new_player(self, name=None, phone=None):
        return EmptyPlayer(name, phone)


class EmptySearch():
    def player(self, name=None, phone=None, name_like=None):
        if name == 'exists':
            return [EmptyPlayer(name, phone)]
        
        if name_like == 'several':
            return [
                EmptyPlayer('several1', '732422322'),
                EmptyPlayer('several2', '732422323'),
                EmptyPlayer('several3', '732422324')
            ]
        
        return []


def test_init():
    s = Session()

    
def test_send_contact_1_known_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage())
    for i in (
        ('game', ''),
        ('game_player_confirm', Contact(name='exists', phone='7823434'))
    ):
        s.process_command(command=i[0], input=i[1])

        
def test_send_contact_1_unknown_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage())
    for i in (
        ('game', ''),
        ('game_player_confirm', Contact(name='notexists', phone='7823435'))
    ):
        s.process_command(command=i[0], input=i[1])
        

def test_add_1_unknown_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage())
    for i in (
        ('game', ''),
        ('', 'notexists'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], input=i[1])


def test_add_1_known_and_1_unknown_player():
    s = Session()
    s.start(search=EmptySearch(), manage=EmptyManage())
    for i in (
        ('game', ''),
        ('game_player_confirm', Contact(name='exists', phone='7823434')),
        ('', 'unknown player'),
        ('game_new_player_phone', '79126632745')
    ):
        s.process_command(command=i[0], input=i[1])