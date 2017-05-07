import xworkflows
import random
from .common_types import Contact, Button
from .telegram_interaction import TelegramInteraction, TelegramInMessage, TelegramOutMessage


# used for parsing request into command with input
# and for composing response
telegram = TelegramInteraction()


class AbstractSession():

    state = None

    # A list of transitions and checks performed on an input without command
    # check returns tuple (index of transition, parsed args)
    # (source state, check, transitions)
    raw_input_transitions = ()
    
    def __init__(self):
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
            print(f'\nERROR: transition not found: {command}')
            return False
            
        args = AbstractSession.parse_input(input)
        transition(args)
        
        return True
    
    def _on_user_raw_input(self, input):
        raw_input_transition = None
        for rit in self.raw_input_transitions:
            if self.state.name == rit[0]:
                raw_input_transition = rit
                break
                
        if raw_input_transition is None:
            return False
            
        check = getattr(self, raw_input_transition[1])
        
        if check is None:
            print(f'\nERROR: check is undefined {raw_input_transition[1]}')
            return False

        args = AbstractSession.parse_input(input)
        
        # check returns tuple (index of target transition or -1 if check fails, parsed arguments)
        c = check(args)
        if c[0] >= 0:
            transition = getattr(self, raw_input_transition[2][c[0]])
            if transition is None:
                print(f'\nERROR: transition is not defined {raw_input_transition[2][c[0]]}')
                return False
            
            transition(c[1])
            return True
        else:
            print('\ncheck failed')
            return False
            
    def process_command(self, command, input):
        if command is not None and len(command) > 0:
            response = self._on_user_command(command, input)
        else:
            response = self._on_user_raw_input(input)

        if not response:
            print(f'\nFailed to process command: \'{command}\' input: \'{input}\'')
            
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
        #print('\n', transition, 'from_state:', from_state)
        pass


class Session(AbstractSession, xworkflows.WorkflowEnabled):

    state = SessionWorkflow()

    def start(self, search, manage):
        
        self.search = search
        self.manage = manage
        
        self._game = None
        self._player = None

    # A list of transitions and checks performed on an input without command
    # check returns tuple (index of transition, parsed args)
    # (source state, check, transitions)
    raw_input_transitions = (
        ('s_game_adding_player', 'check_adding_player', ('game_player_confirm', 'game_add_new_player')),
        ('s_game_new_player_phone', 'check_adding_players_phone', 'game_new_player_phone')
    )
    
    ''' Checks '''
    # return tuple (index of transition, parsed arguments)
    def check_adding_player(self, args):
        if type(args[0]) == Contact:
            return (0, args[0])
            
        players = self.search.player(name_like=args[0])
        if len(players) == 1:
            return (0, players[0])
        else:
            return (1, Contact(name=args[0], phone=None))

    def check_adding_players_phone(self, args):
        try:
            phone = int(self._normalize_phone(args))
            return (0, str(phone))
        except ValueError:
            # show message error
            return (-1)

    ''' Transitions '''
    @xworkflows.transition()
    def game(self, args):
        self._game = self.manage.new_game()
        
    @xworkflows.transition()
    def game_player_confirm(self, player):
        if type(player) == Contact:
            player = self.search.player(name=player.name, phone=player.phone)

        self._player = player
    
    @xworkflows.transition()
    def game_add_new_player(self, contact):
        self._player = self.manage.new_player(name=contact.name)
        
    @xworkflows.transition()
    def game_new_player_phone(self, args):
        self._player.phone = self._normalize_phone(args)
        
    @xworkflows.on_enter_state('s_game_player_confirmed')
    def _on_s_game_player_confirmed(self, res, *args, **kwargs):
        self._add_player_to_game()
        # TODO should check if enough players
        # now continue adding forever
        self.game_next_player()
    
    @xworkflows.on_enter_state('s_game_adding_player')
    def _on_s_game_adding_player(self, res, *args, **kwargs):
        # TODO show message 'enter player name or push search button'
        pass
    
    def _normalize_phone(self, args):
        # TODO remove spaces
        return args[0]
    
    def _add_player_to_game(self):
        # TODO add self._player to self._game
        # show message about it
        pass