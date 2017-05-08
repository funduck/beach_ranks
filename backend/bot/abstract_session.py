import logging
import sys
import xworkflows
from .common_types import Contact
from .telegram_interaction import TelegramInteraction, TelegramInMessage, TelegramOutMessage

# used for parsing request into command with input
# and for composing response
telegram = TelegramInteraction()

logger = logging.getLogger('AbstractSession')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(0)
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

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
    def show_message(self, message=None, buttons=None, processing_message=None):
        if processing_message is not None:
            as_reply = processing_message.ids
        else:
            # this will lead to exception
            as_reply = None
        m = telegram.show_message(as_reply, message, buttons)
        
        logger.debug(m)
        
        self.responses.append(m)
    
    # creates message via telegram_interactions and puts to resposes
    def show_contacts(self, contacts, processing_message=None):
        if processing_message is not None:
            as_reply = processing_message.ids
        else:
            # this will lead to exception
            as_reply = None
        m = telegram.show_contacts(as_reply, contacts)
        
        logger.debug(m)
        
        self.responses.append(m)
    
    @staticmethod
    def parse_input(input):
        if input is None:
            return None
            
        if type(input) == Contact:
            return input
            
        return input.split(' ')
    
    def _on_user_command(self, command, input, processing_message=None):
        if command is None:
            return False
            
        transition = getattr(self, command)
        if transition is None:
            logger.error(f'transition not found: {command}')
            return False
            
        args = AbstractSession.parse_input(input)
        transition(args, processing_message)
        
        return True
    
    def _on_user_raw_input(self, input, processing_message=None):
        raw_input_transition = None
        for rit in self.raw_input_transitions:
            if self.state.name == rit[0]:
                raw_input_transition = rit
                break
                
        if raw_input_transition is None:
            return False
            
        check = getattr(self, raw_input_transition[1])
        
        if check is None:
            logger.error(f'check is undefined {raw_input_transition[1]}')
            return False

        args = AbstractSession.parse_input(input)
        
        # check returns tuple (index of target transition or -1 if check fails, parsed arguments)
        c = check(args, processing_message)
        if c[0] >= 0:
            if type(raw_input_transition[2]) == tuple:
                if c[0] >= len(raw_input_transition[2]):
                    logger.error(f'check returned > number of options \'{raw_input_transition}\'')
                    return False
                else:
                    transition_name = raw_input_transition[2][c[0]]
            else:
                if c[0] > 0:
                    logger.error(f'check returned >0, while there is only 1 option \'{raw_input_transition}\'')
                    return False
                else:
                    transition_name = raw_input_transition[2]
            transition = getattr(self, transition_name)
            if transition is None:
                logger.error(f'transition is not defined \'{transition_name}\'')
                return False
            
            transition(c[1], processing_message)
            return True
        else:
            logger.debug(f'check \'{raw_input_transition[1]}\' refused')
            return False
            
    def process_command(self, command, input, processing_message=None):
        logger.info(f'Processing command: \'{command}\' \'{input}\'')
        
        if command is not None and len(command) > 0:
            response = self._on_user_command(command, input, processing_message)
        else:
            response = self._on_user_raw_input(input, processing_message)

        if not response:
            logger.info(f'Refused to process command: \'{command}\' input: \'{input}\'')
        
        return response
            
    # returns array of responses, should be performed in asc order
    # usually will contain only 1 item
    def process_request(self, r, bot_name='beachranks_bot'):
        logger.info(f'Processing request: \'{r}\' \'{bot_name}\'')
        
        m = telegram.parse_message(message=r, bot_name=bot_name)
        
        if self.process_command(command=m.command, input=m.input, processing_message=m):
            responses = self.responses
            self.responses = []
            return responses
        
        return []