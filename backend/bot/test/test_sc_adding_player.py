import pytest

from bot.sc_adding_player import AddingPlayer, PlayerContact


class Environment():
    buttons = None
    contacts = None

    def like(self, input):
        known = ['Ivanov', 'Ivanovich', 'Ivan', 'Ivanesco', 'Iveta']
        res = []
        for i in known:
            if i.startswith(input):
                res.append(PlayerContact(name=i, phone='7901312378'+str(len(i))))
        return res

    def show_message(self, message=None, buttons=None, as_reply=None):
        print('Bot says:', message)
        self.buttons = buttons
        
    def show_contacts(self, contacts=None, as_reply=None):
        self.contacts = contacts
        

def test_adding_player_scenario_choose():
    print('\n *** TEST START1 ***')
    env = Environment()
    
    def done(choice):
        assert choice is not None
        assert choice.name == 'Ivanov'
        
    adding = AddingPlayer(player_search=env, user_interaction=env, on_done=done)
    
    adding.start()
    adding.on_user_inline_input(input='Iva')
    # press 1st in list
    adding.on_user_input(command='player', input=env.contacts[0])


def test_adding_player_scenario_add_new():
    print('\n *** TEST START2 ***')
    env = Environment()
    
    def done(choice):
        assert choice is not None
        assert choice.name == 'New'
        
    adding = AddingPlayer(player_search=env, user_interaction=env, on_done=done)
    
    adding.start()
    assert adding.state.is_choosing
    adding.on_user_inline_input(input='New')
    adding.on_user_input(command='player', input='New')
    assert adding.state.is_adding_new_player
    adding.on_user_input(input='79031327637')
    env.buttons[0].callback(env.buttons[0].arg)
    

def test_adding_player_scenario_do_anything_wrong():
    print('\n *** TEST START3 ***')
    env = Environment()
    
    def done(choice):
        assert choice.name == 'New'
        assert choice.phone == '79031327637'
        
    adding = AddingPlayer(player_search=env, user_interaction=env, on_done=done)
    
    adding.start()
    assert adding.state.is_choosing
    
    # random actions
    adding.on_user_confirm(args={'as_reply':None})
    assert adding.state.is_choosing
    adding.on_user_input(input='79031327636')
    assert adding.state.is_choosing
    adding.on_user_inline_input(input='New')
    assert adding.state.is_choosing
    adding.cancel()
    assert adding.state.is_init
    adding.on_user_input(input='79031327637')
    assert adding.state.is_init
    adding.start()
    assert adding.state.is_choosing
    #
    
    adding.on_user_inline_input(command='player', input='New')
    adding.on_user_input(command='player', input='New')
    assert adding.state.is_adding_new_player
    adding.on_user_input(input='79031327637')
    env.buttons[0].callback(env.buttons[0].arg)