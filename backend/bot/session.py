import xworkflows
import logging
import sys
from model import Player
from model import Game
from .common_types import Button
from .abstract_session import AbstractSession
from .telegram_interaction import TelegramInteraction, TelegramInMessage, TelegramOutMessage


logger = logging.getLogger('Session')
logger.setLevel(logging.INFO)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(0)
formatter = logging.Formatter('%(asctime)s  %(name)s  %(levelname)s  %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)


class SessionWorkflow(xworkflows.Workflow):
    # A list of state names, adding 's_' helps to ease reading
    states = (
        ('init', 'Init state'),
        ('s_game_adding_player', 'Adding player in a game'),
        ('s_game_player_confirmed', 'Add player to game success'),
        ('s_game_new_player_phone', 'Adding phone for new player in a game'),
        ('s_game_set_won_score', 'Setting score of a winner'),
        ('s_game_set_lost_score', 'Setting score of a looser'),
        ('s_game_created', 'All fields of Game are filled')
    )
    
    # Transition names are bot commands
    # A list of transition definitions
    # (transition, source states, target state).
    transitions = (
        ('game', 'init', 's_game_adding_player'),
        ('find_player', 's_game_adding_player', 's_game_adding_player'),
        ('game_player_confirm', 's_game_adding_player', 's_game_player_confirmed'),
        ('game_add_new_player', 's_game_adding_player', 's_game_new_player_phone'),
        ('game_new_player_phone', 's_game_new_player_phone', 's_game_player_confirmed'),
        ('game_next_player', 's_game_player_confirmed', 's_game_adding_player'),
        ('game_set_scores', 's_game_player_confirmed', 's_game_set_won_score'),
        ('game_set_score_won', 's_game_set_won_score', 's_game_set_lost_score'),
        ('game_set_score_lost', 's_game_set_lost_score', 's_game_created'),
        ('game_save', 's_game_created', 'init')
    )
    initial_state = 'init'
    
    def log_transition(self, transition, from_state, instance, *args, **kwargs):
        logger.log(0, f'\'{transition}\' from_state \'{from_state}\'')


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
        ('s_game_new_player_phone', 'check_adding_players_phone', ('game_new_player_phone')),
        ('s_game_set_won_score', 'check_setting_score', ('game_set_score_won')),
        ('s_game_set_lost_score', 'check_setting_score', ('game_set_score_lost'))
    )
    
    ''' Checks '''
    # return tuple (index of transition, parsed arguments)
    def check_adding_player(self, args, processing_message=None):
        if type(args) == Player:
            return (0, args)
        
        players = self.search.player(name_like=args[0])
        if len(players) == 1:
            return (0, players[0])
        else:
            return (1, Player(nick=args[0], phone=None))

    def check_adding_players_phone(self, args, processing_message=None):
        try:
            phone = int(self._normalize_phone(args))
            return (0, str(phone))
        except ValueError:
            self.show_message(
                message='Phone number is incorrect',
                processing_message=processing_message
            )
            return (-1, None)
            
    def check_setting_score(self, args, processing_message=None):
        try:
            score = int(args[0])
            if score >= 0:
                if self.state.is_s_game_set_lost_score or score > 14:
                    if self.state.is_s_game_set_lost_score and score + 1 >= self._game.score_won:
                        self.show_message(
                            message='Score of a looser +1 should be < score of a winner',
                            processing_message=processing_message
                        )
                        return (-1, None)
                    return (0, score)
                else:
                    self.show_message(
                        message='Score of a winner should be >= 15',
                        processing_message=processing_message
                    )
                    return (-1, None)
            else:
                self.show_message(
                    message='Score should be >= 0',
                    processing_message=processing_message
                )
                return (-1, None)
        except ValueError:
            self.show_message(
                message='Score is not a number',
                processing_message=processing_message
            )
            return (-1, None)

    ''' Transitions '''
    @xworkflows.transition()
    def game(self, args=None, processing_message=None):
        self._game = Game()
        self.show_message(
            message='Adding game\n1) enter players, won team, then lost\n2) enter scores, won first',
            processing_message=processing_message
        )
        
    @xworkflows.transition()
    def find_player(self, args=None, processing_message=None):
        if args is not None and len(args[0]) > 0:
            players = self.search.player(name_like=args[0])
            self.show_contacts(
                contacts=players, 
                processing_message=processing_message
            )

    @xworkflows.transition()
    def game_player_confirm(self, player, processing_message=None):
        self._player = player
    
    @xworkflows.transition()
    def game_add_new_player(self, player, processing_message=None):
        self._player = player
        self.show_message(
            message='Someone new, enter his phone number',
            processing_message=processing_message
        )
        
    @xworkflows.transition()
    def game_new_player_phone(self, phone, processing_message=None):
        self._player.phone = self._normalize_phone(phone)
        
    @xworkflows.transition()
    def game_set_score_won(self, score, processing_message=None):
        self._game.score_won = score
        self.show_message(
            message='Ok, now score of a looser',
            processing_message=processing_message
        )
    
    @xworkflows.transition()
    def game_set_score_lost(self, score, processing_message=None):
        self._game.score_lost = score
        self.show_message(
            message='Ok, done with scores',
            processing_message=processing_message
        )
    
    @xworkflows.transition()
    def game_set_scores(self, arg=None, processing_message=None):
        self.show_message(
            message='Enter score of a winner',
            processing_message=processing_message
        )
        
    @xworkflows.transition()
    def game_next_player(self, arg=None, processing_message=None):
        pass
        
    @xworkflows.transition()
    def game_save(self, processing_message=None):
        self.manage.save_game(game=self._game, who=processing_message.ids.user_id)
        self.show_message(
            message='Game saved',
            processing_message=processing_message
        )
    
    @xworkflows.on_enter_state('s_game_player_confirmed')
    def _on_s_game_player_confirmed(self, transition_res=None, transition_arg=None, processing_message=None):
        self._add_player_to_game()
        self.show_message(
            message='Player added',
            processing_message=processing_message
        )
        if len(self._game.nicks_won) < 2 or len(self._game.nicks_lost) < 2:
            self.game_next_player(processing_message=processing_message)
        else:
            self.game_set_scores(processing_message=processing_message)
    
    @xworkflows.on_enter_state('s_game_adding_player')
    def _on_s_game_adding_player(self, transition_res=None, transition_arg=None, processing_message=None):
        self.show_message(
            message='Enter player\'s name',
            buttons=[Button(
                text='search',
                switch_inline='/find_player ',
                callback=None
            )],
            processing_message=processing_message
        )
    
    @xworkflows.on_enter_state('s_game_created')
    def _on_s_game_created(self, transition_res=None, transition_arg=None, processing_message=None):
        self.game_save(processing_message)
    
    def _normalize_phone(self, args=None):
        p = ''
        for i in args:
            p = p + i
        return p.replace(' ', '')
    
    def _add_player_to_game(self):
        g = self._game
        if len(g.nicks_won) < 2:
            g.nicks_won.append(self._player.nick)
        else:
            if len(g.nicks_lost) < 2:
                g.nicks_lost.append(self._player.nick)