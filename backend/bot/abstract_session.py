import xworkflows
from .common_types import Contact


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
                print(f'\nERROR: transition is not defined \'{raw_input_transition[2][c[0]]}\'')
                return False
            
            transition(c[1])
            return True
        else:
            print(f'\ncheck \'{raw_input_transition[1]}\' failed')
            return False
            
    def process_command(self, command, input):
        print(f'\nProcessing command: \'{command}\' \'{input}\'')
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