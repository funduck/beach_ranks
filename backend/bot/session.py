import xworkflows
import random
from .common_types import Contact, Button
from .telegram_interaction import TelegramInteraction, TelegramInMessage, TelegramOutMessage


# used for parsing request into command with input
# and for composing response
telegram = TelegramInteraction()


class AbstractSession():
    def __init__(self):
        self.state = None
        # queue of responses
        self.responses = []
        
    # creates message via telegram_interactions and puts to resposes
    def show_message(self, as_reply, message=None, buttons=None):
        self.responses.append(
            telegram.show_message(as_reply, message, buttons)
        )
    
    # creates message via telegram_interactions and puts to resposes
    def show_contacts(self, as_reply, contacts):
        self.responses.append(
            telegram.show_contacts(as_reply, contacts)
        )
    
    @staticmethod
    def parse_input(input):
        if input is None:
            return None
            
        if type(input) == Contact:
            return input
            
        return input.split(' ')
    
    def _on_user_command(self, command, input):
        if command is None:
            return False
            
        transition = getattr(self, command)
        if transition is None:
            return False
            
        args = AbstractSession.parse_input(input)
        transition(args)
        
        return True
    
    def _on_user_raw_input(self, input):
        raw_input_transition = None
        for t in self.raw_input_transitions:
            if self.state.name == self.raw_input_transitions[t][0]:
                raw_input_transition = self.raw_input_transitions
                break
                
        if raw_input_transition is None:
            return False
            
        check = getattr(self, raw_input_transition[1])
        
        if check is None:
            print('\nERROR: ', 'check is undefined', raw_input_transition[1])
            return False

        args = AbstractSession.parse_input(input)
        
        # check returns index of target transition or -1 if check fails
        c = check(args)
        if c > 0:
            transition = getattr(self, raw_input_transition[2][c])
            if transition is None:
                print('\nERROR: ', 'transition is not defined', raw_input_transition[2][c])
                return False
            
            transition(args)
            return True
        else:
            print('\ncheck failed')
            return False
            
    def process_command(self, command, input):
        if command is not None:
            response = self._on_user_command(command, input)
        else:
            response = self._on_user_raw_input(input)

        if not response:
            print('\nFailed to process command: \'{command}\' input: \'{input}\'')
            
        return response
            
    # returns array of responses, should be performed in asc order
    # usually will contain only 1 item
    def process_request(self, r, bot_name='beachranks_bot'):
        m = telegram.parse_message(message=r, bot_name=bot_name)
        
        if self.process_command(command=m.command, input=m.input):
            responses = self.responses
            self.responses = []
            return responses
        
        return []

class SessionWorkflow(xworkflows.Workflow):
    # A list of state names, adding 's_' helps to ease reading
    states = (
        ('init', 'Init state'),
        ('s_game_adding_player', 'Adding player in a game'),
        ('s_game_player_confirmed', 'Add player to game success'),
        ('s_game_new_player_phone', 'Adding phone for new player in a game')
    )
    
    # Transition names are bot commands
    # A list of transition definitions
    # (transition, source states, target state).
    transitions = (
        ('game', 'init', 's_game_adding_player'),
        ('game_player_confirm', 's_game_adding_player', 's_game_player_confirmed'),
        ('game_add_new_player', 's_game_adding_player', 's_game_new_player_phone'),
        ('game_new_player_phone', 's_game_new_player_phone', 's_game_player_confirmed'),
        ('game_next_player', 's_game_player_confirmed', 's_game_adding_player')
    )
    initial_state = 'init'
    
    def log_transition(self, transition, from_state, instance, *args, **kwargs):
        # print('\n', transition, 'from_state:', from_state)
        pass


class Session(AbstractSession, xworkflows.WorkflowEnabled):

    def start(self):
        self.state = SessionWorkflow()

    # A list of transitions and checks performed on an input without command
    # check returns index of transition, like switch
    # (source state, check, transitions)
    raw_input_transitions = (
        ('s_game_adding_player', 'check_adding_player', ('game_player_confirm', 'game_add_new_player')),
        ('s_game_new_player_phone', 'check_adding_players_phone', ('game_new_player_phone', 'game_player_confirm'))
    )
    
    ''' Checks '''
    def check_adding_player(self, args):
        return 0

    def check_adding_players_phone(self, args):
        return 1

    ''' Transitions '''
    @xworkflows.transition()
    def game(self, args):
        pass
        
    @xworkflows.transition()
    def game_player_confirm(self, args):
        pass
        
    @xworkflows.transition()
    def game_add_new_player(self, args):
        pass
        
    @xworkflows.transition()
    def game_new_player_phone(self, args):
        pass
        
    @xworkflows.on_enter_state('s_game_player_confirmed')
    def _on_s_game_player_confirmed(self, res, *args, **kwargs):
        # TODO should check there are enough players
        # now continue adding forever
        self.game_next_player()