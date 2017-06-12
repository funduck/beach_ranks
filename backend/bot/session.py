import json
import xworkflows
import logging

from common import initLogger
from model import Player
from model import Game
from .types import Button
from .abstract_session import AbstractSession
from .telegram_interaction import TelegramInteraction, TelegramInMessage, TelegramOutMessage


logger = initLogger('BotSession')


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

    def start(self, backend, text):
        logger.debug('start')
        self.backend = backend
        self.text = text

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

    def _check_error_is_fatal(self, err):
        if err is not None and err['error_type'] != 'negative response':
            raise RuntimeError(json.dumps(err))

    ''' Checks '''
    # return tuple (index of transition, parsed arguments)
    def check_adding_player(self, input, processing_message=None):
        if type(input) == Player:
            return (0, input)

        err, player = self.backend.get_player(nick=input)
        self._check_error_is_fatal(err)
        if player is not None:
            return (0, player)
        else:
            return (1, Player(nick=input, phone=None))

    def check_adding_players_phone(self, input, processing_message=None):
        try:
            phone = int(self._normalize_phone(input))
            return (0, str(phone))
        except ValueError:
            self.show_message(
                message=self.text.phone_incorrect(),
                processing_message=processing_message,
                reply=True
            )
            return (-1, None)

    def check_setting_score(self, input, processing_message=None):
        try:
            score = int(input)
            if score >= 0:
                if self.state.is_s_game_set_lost_score or score > 14:
                    if self.state.is_s_game_set_lost_score and score + 1 >= self._game.score_won:
                        self.show_message(
                            message=self.text.score_looser_less_than_winner(),
                            processing_message=processing_message,
                            reply=True
                        )
                        return (-1, None)
                    return (0, score)
                else:
                    self.show_message(
                        message=self.text.score_winner_min_value(),
                        processing_message=processing_message,
                        reply=True
                    )
                    return (-1, None)
            else:
                self.show_message(
                    message=self.text.score_min_value(),
                    processing_message=processing_message,
                    reply=True
                )
                return (-1, None)
        except ValueError:
            self.show_message(
                message=self.text.score_is_not_a_number(),
                processing_message=processing_message,
                reply=True
            )
            return (-1, None)

    ''' Transitions '''
    @xworkflows.transition()
    def game(self, input=None, processing_message=None):
        logger.debug('game')
        self._game = Game()
        self.show_message(
            message=self.text.game_add_start(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def find_player(self, input=None, processing_message=None):
        logger.debug('find_player')
        if input is not None and len(input) > 1:
            err, players = self.backend.get_players(nick_like=input)
            self._check_error_is_fatal(err)
            self.show_contacts(
                contacts=players,
                processing_message=processing_message
            )

    @xworkflows.transition()
    def game_player_confirm(self, player, processing_message=None):
        logger.debug('game_player_confirm')
        self._player = player

    @xworkflows.transition()
    def game_add_new_player(self, player, processing_message=None):
        logger.debug('game_add_new_player')
        self._player = player
        self.show_message(
            message=self.text.player_adding_someone_new(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def game_new_player_phone(self, phone, processing_message=None):
        logger.debug('game_new_player_phone')
        self._player.phone = self._normalize_phone(phone)

    @xworkflows.transition()
    def game_set_score_won(self, score, processing_message=None):
        logger.debug('game_set_score_won')
        self._game.score_won = score
        self.show_message(
            message=self.text.score_winner_set_next_looser(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def game_set_score_lost(self, score, processing_message=None):
        logger.debug('game_set_score_lost')
        self._game.score_lost = score
        '''self.show_message(
            message=self.text.score_set_done(),
            processing_message=processing_message
        )'''

    @xworkflows.transition()
    def game_set_scores(self, arg=None, processing_message=None):
        logger.debug('game_set_scores')
        self.show_message(
            message=self.text.score_set_winner(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def game_next_player(self, arg=None, processing_message=None):
        logger.debug('game_next_player')
        pass

    @xworkflows.transition()
    def game_save(self, processing_message=None):
        logger.debug('game_save')
        err, g = self.backend.add_game(game=self._game, who=processing_message.ids.user_id)
        self._check_error_is_fatal(err)
        self._game = g
        self.show_message(
            message=self.text.game_saved(),
            processing_message=processing_message
        )

    @xworkflows.on_enter_state('s_game_player_confirmed')
    def _on_s_game_player_confirmed(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_game_player_confirmed')
        self._add_player_to_game()
        self.show_message(
            message=self.text.player_added(),
            processing_message=processing_message
        )
        if len(self._game.nicks_won) < 2 or len(self._game.nicks_lost) < 2:
            self.game_next_player(processing_message=processing_message)
        else:
            self.game_set_scores(processing_message=processing_message)

    @xworkflows.on_enter_state('s_game_adding_player')
    def _on_s_game_adding_player(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_game_adding_player')
        self.show_message(
            message=self.text.game_add_next_player(self._game),
            buttons=[Button(
                text='search',
                switch_inline='/find_player ',
                callback=None
            )],
            processing_message=processing_message
        )

    @xworkflows.on_enter_state('s_game_created')
    def _on_s_game_created(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_game_created')
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
