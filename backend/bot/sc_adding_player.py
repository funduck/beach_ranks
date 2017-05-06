import xworkflows
import random
from .ui_types import PlayerContact, UIButton


class AddingPlayerWorkflow(xworkflows.Workflow):
    # A list of state names
    states = (
        ('init', 'Init state'),
        ('choosing', 'Choosing among players known to bot'),
        ('adding_new_player', 'Adding a player new to bot'),
        ('confirming', 'Waiting for user\'s confirm')
    )
    # A list of transition definitions; items are (name, source states, target).
    transitions = (
        ('start', ('init', 'confirming'), 'choosing'),
        ('add_unknown_player', 'choosing', 'adding_new_player'),
        ('ask_confirm_choice', 'choosing', 'confirming'),
        ('ask_confirm_phone', 'adding_new_player', 'confirming'),
        ('confirm_player', ('confirming', 'choosing'), 'init'),
        ('cancel', ('adding_new_player', 'choosing'), 'init')
    )
    initial_state = 'init'
    
    def log_transition(self, transition, from_state, instance, *args, **kwargs):
        print('\n', transition, 'from_state:', from_state)


# scenario in which bot adds a player
class AddingPlayer(xworkflows.WorkflowEnabled):
    state = AddingPlayerWorkflow()
    choice = None
    player_search = None
    user_interaction = None
    on_done = None

    def __init__(self, player_search, user_interaction, on_done):
        self.choice = None
        self.player_search = player_search
        self.user_interaction = user_interaction
        self.user_interaction.on_user_input = self.on_user_input
        self.user_interaction.on_user_inline_input = self.on_user_inline_input
        self.on_done = on_done

    ''' User input '''
    def check_input_player(self, input):
        print('check_input_player:', input)
        
        if type(input) == PlayerContact:
            print('check_input_player, it is PlayerContact')
            return input

        found = self.player_search.like(input)
        if len(found) == 1:
            print('check_input_player, search found one')
            return found[0]
        else:
            print('check_input_player, found none')
            try:
                int(input)
                print('check_input_player, it is number')
                return False
            except ValueError:
                print('check_input_player, it is fine')
                return True
                
    def check_input_phone(self, input):
        try:
            int(input)
            return True
        except ValueError:
            return False
    
    def on_user_input(self, command=None, input=None, as_reply=None):
        if command == 'player' and (input is None or len(input) == 0):
            return self.start(as_reply)

        if self.state.is_choosing and (command == 'player' or command is None):
            found = self.check_input_player(input)
            if not found:
                self.user_interaction.show_message(
                    message=f'It\'s incorrect player name: {input}',
                    as_reply=as_reply
                )
                return
            if found == True:
                self.add_unknown_player(input, as_reply)
                return
            else:
                self.ask_confirm_choice(found, as_reply)
                return
        
        if self.state.is_adding_new_player and command is None:
            if self.check_input_phone(input):
                self.ask_confirm_phone(input, as_reply)
                return
            else:
                self.user_interaction.show_message(
                    message=f'It\'s incorrect phone number: {input}', 
                    as_reply=as_reply
                )
                return
        
        self.user_interaction.show_message(
            message='I beg you pardon?' if random.randint(0, 1) == 0 else 'Pardon me?', 
            as_reply=as_reply
        )

    def on_user_inline_input(self, command=None, input=None, as_reply=None):
        found = self.player_search.like(input)
        if len(found) > 0:
            contact_list = []
            for player in found:
                contact_list.append(player)
            self.user_interaction.show_contacts(
                contacts=contact_list,
                as_reply=as_reply
            )

    # check for confirm_player
    def on_user_confirm(self, args):
        if args is None:
            print('ERROR: args is None or dont have \'as_reply\', what to confirm?')
            return
            
        if 'player' not in args and self.choice is None:
            self.user_interaction.show_message(
                message=f'Oops, I have nothing to confirm',
                as_reply=args['as_reply']
            )
            return

        self.confirm_player(args)

    ''' Transitions of state machine '''
    @xworkflows.transition()
    def start(self, as_reply=None):
        self.choice = None
        self.user_interaction.show_message(
            message='Enter player\'s name',
            buttons=[UIButton(
                text='search',
                switch_inline='/player ', # '/player ' added in self.user_interaction, and removed before on_user_inline_input also somewhere outside
                callback=None,
                arg=None
            )],
            as_reply=as_reply
        )
    
    @xworkflows.transition()
    def ask_confirm_choice(self, choice, as_reply=None):
        self.user_interaction.show_message(
            message=f'{choice.name} {choice.phone},\nadd?',
            buttons=[UIButton(
                text='confirm',
                switch_inline=None,
                callback=self.on_user_confirm, # callback function is always with one argument
                arg={ # one argument of a callback
                    'player': choice,
                    'as_reply': as_reply
                }
            )],
            as_reply=as_reply
        )
        
    @xworkflows.transition()
    def ask_confirm_phone(self, input, as_reply=None):
        self.choice = PlayerContact(name=self.choice.name, phone=input)
        self.user_interaction.show_message(
            message='Confirm player\'s phone',
            buttons=[UIButton(
                text='confirm',
                switch_inline=None,
                callback=self.on_user_confirm, # callback function is always with one argument
                arg={ # one argument of a callback
                    'player': self.choice,
                    'as_reply': as_reply
                }
            )],
            as_reply=as_reply
        )
    
    @xworkflows.transition()
    def confirm_player(self, args):
        if 'player' in args:
            self.choice = args['player']
            
        self.user_interaction.show_message(
            message=f'Added {self.choice.name} {self.choice.phone}',
            as_reply=args['as_reply']
        )
        self.on_done(self.choice)
        
    @xworkflows.transition()
    def add_unknown_player(self, input, as_reply=None):
        self.choice = PlayerContact(name=input, phone='')
        self.user_interaction.show_message(
            message='It\'s someone I don\'t know\nenter the phone number',
            as_reply=as_reply
        )
        
    @xworkflows.transition()
    def cancel(self, as_reply=None):
        self.user_interaction.show_message(
            message=f'\'{self.state.title}\' canceled',
            as_reply=as_reply
        )
    
    @xworkflows.transition()
    def cancel_confirm(self, as_reply=None):
        self.user_interaction.show_message(
            message=f'\'{self.state.title}\' canceled',
            as_reply=as_reply
        )