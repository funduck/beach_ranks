import xworkflows
from .common_types import Contact, Button
from .abstract_session import AbstractSession
from .telegram_interaction import TelegramInteraction, TelegramInMessage, TelegramOutMessage

class SessionWorkflow(xworkflows.Workflow):
    # A list of state names, adding 's_' helps to ease reading
    states = (
        ('init', 'Init state'),
        ('s_game_adding_player', 'Adding player in a game'),
        ('s_game_player_confirmed', 'Add player to game success'),
        ('s_game_new_player_phone', 'Adding phone for new player in a game'),
        ('s_game_set_won_score', 'Setting score of a winner'),
        ('s_game_set_lost_score', 'Setting score of a looser')
    )
    
    # Transition names are bot commands
    # A list of transition definitions
    # (transition, source states, target state).
    transitions = (
        ('game', 'init', 's_game_adding_player'),
        ('game_player_confirm', 's_game_adding_player', 's_game_player_confirmed'),
        ('game_add_new_player', 's_game_adding_player', 's_game_new_player_phone'),
        ('game_new_player_phone', 's_game_new_player_phone', 's_game_player_confirmed'),
        ('game_next_player', 's_game_player_confirmed', 's_game_adding_player'),
        ('game_set_scores', 's_game_player_confirmed', 's_game_set_won_score'),
        ('game_set_score_won', 's_game_set_won_score', 's_game_set_lost_score'),
        ('game_set_score_lost', 's_game_set_lost_score', 'init')
    )
    initial_state = 'init'
    
    def log_transition(self, transition, from_state, instance, *args, **kwargs):
        print('\n', transition, 'from_state:', from_state)


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
        if type(args[0]) == Contact:
            return (0, args[0])
            
        players = self.search.player(name_like=args[0])
        if len(players) == 1:
            return (0, players[0])
        else:
            return (1, Contact(name=args[0], phone=None))

    def check_adding_players_phone(self, args, processing_message=None):
        try:
            phone = int(self._normalize_phone(args))
            return (0, str(phone))
        except ValueError:
            # show message error
            return (-1, None)
            
    def check_setting_score(self, args, processing_message=None):
        try:
            int(args[0])
            return (0, args[0])
        except ValueError:
            # show message error
            return (-1, None)

    ''' Transitions '''
    @xworkflows.transition()
    def game(self, args=None, processing_message=None):
        self._game = self.manage.new_game()
        
    @xworkflows.transition()
    def game_player_confirm(self, player, processing_message=None):
        if type(player) == Contact:
            player = self.search.player(name=player.name, phone=player.phone)

        self._player = player
    
    @xworkflows.transition()
    def game_add_new_player(self, contact, processing_message=None):
        self._player = self.manage.new_player(name=contact.name)
        
    @xworkflows.transition()
    def game_new_player_phone(self, phone, processing_message=None):
        self._player.phone = self._normalize_phone(phone)
        
    @xworkflows.transition()
    def game_set_score_won(self, score, processing_message=None):
        self._game.score_won = score
    
    @xworkflows.transition()
    def game_set_score_lost(self, score, processing_message=None):
        self._game.score_lost = score
        pass
    
    @xworkflows.transition()
    def game_set_scores(self, arg=None, processing_message=None):
        pass
        
    @xworkflows.transition()
    def game_next_player(self, arg=None, processing_message=None):
        pass
        
    @xworkflows.on_enter_state('s_game_player_confirmed')
    def _on_s_game_player_confirmed(self, transition_res=None, transition_arg=None, processing_message=None):
        self._add_player_to_game()
        if len(self._game.team_won) < 2 or len(self._game.team_lost) < 2:
            self.game_next_player(processing_message=processing_message)
        else:
            print(f'\nAll players added: {self._game.team_won} {self._game.team_lost}')
            self.game_set_scores(processing_message=processing_message)
    
    @xworkflows.on_enter_state('s_game_adding_player')
    def _on_s_game_adding_player(self, transition_res=None, transition_arg=None, processing_message=None):
        self.show_message(
            message='Enter player\'s name',
            buttons=[Button(
                text='search',
                switch_inline='/player ',
                callback=None
            )],
            processing_message=processing_message
        )
    
    def _normalize_phone(self, args=None):
        p = ''
        for i in args:
            p = p + i
        return p.replace(' ', '')
    
    def _add_player_to_game(self):
        g = self._game
        if len(g.team_won) < 2:
            g.team_won.append(self._player)
        else:
            if len(g.team_lost) < 2:
                g.team_lost.append(self._player)
        print(f'\nPlayer added: \'{self._game.team_won}\' \'{self._game.team_lost}\'')
        # show message about it
        pass