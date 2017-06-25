import json

import xworkflows
from common.model import Game, Player

from common.logger import init_logger
from .abstract_session import AbstractSession
from .elements import Button

logger = init_logger('BotSession')


class SessionWorkflow(xworkflows.Workflow):
    # A list of state names, adding 's_' helps to ease reading
    states = (
        ('init', 'Init state'),
        ('s_game_adding_player', 'Adding player in a game'),
        ('s_game_player_confirmed', 'Add player to game success'),
        ('s_game_new_player_phone', 'Adding phone for new player in a game'),
        ('s_game_set_won_score', 'Setting score of a winner'),
        ('s_game_set_lost_score', 'Setting score of a looser'),
        ('s_game_created', 'All fields of Game are filled'),
        ('s_nick_adding_player', 'Adding player to database'),
        ('s_nick_new_player_phone', 'Adding phone for new player'),
        ('s_players', 'Searching for player'),
        ('s_games', 'Searching for games')
    )

    # A list of transition definitions
    # Transition names are bot commands
    # (transition, source states, target state).
    transitions = (
        ('game_add', 'init', 's_game_adding_player'),
        ('game_player_confirm', 's_game_adding_player', 's_game_player_confirmed'),
        ('game_add_new_player', 's_game_adding_player', 's_game_new_player_phone'),
        ('game_new_player_phone', 's_game_new_player_phone', 's_game_player_confirmed'),
        ('game_next_player', 's_game_player_confirmed', 's_game_adding_player'),
        ('game_set_scores', 's_game_player_confirmed', 's_game_set_won_score'),
        ('game_set_score_won', 's_game_set_won_score', 's_game_set_lost_score'),
        ('game_set_score_lost', 's_game_set_lost_score', 's_game_created'),
        ('game_save', 's_game_created', 'init'),
        ('nick', 'init', 's_nick_adding_player'),
        ('nick_already_exists', 's_nick_adding_player', 'init'),
        ('nick_new_player', 's_nick_adding_player', 's_nick_new_player_phone'),
        ('nick_new_player_phone', 's_nick_new_player_phone', 'init'),
        ('players_wait', 'init', 's_players'),
        ('players_found', 's_players', 'init'),
        ('players_not_found', 's_players', 'init'),
        ('games_wait', 'init', 's_games'),
        ('games_found', 's_games', 'init'),
        ('games_not_found', 's_games', 'init'),
        ('goto_init', ('init', 's_game_created', 's_game_set_lost_score', 's_game_set_won_score',
            's_game_player_confirmed', 's_game_new_player_phone', 's_game_adding_player',
            's_nick_adding_player', 's_nick_new_player_phone', 's_players', 's_games'),
        'init')
    )
    initial_state = 'init'

    def log_transition(self, transition, from_state, instance, *args, **kwargs):
        logger.log(0, f'\'{transition}\' from_state \'{from_state}\'')


class Session(AbstractSession, xworkflows.WorkflowEnabled):
    state = SessionWorkflow()

    def __init__(self, backend, text):
        AbstractSession.__init__(self)
        logger.debug('start')
        self.backend = backend
        self.text = text

        self._game = None
        self._player = None

    # A list of transitions and checks performed on an user_input without command
    # check returns tuple (index of transition, parsed args)
    # (source state, check, transitions)
    raw_input_transitions = (
        ('s_game_adding_player', 'check_adding_player', ('game_player_confirm', 'game_add_new_player')),
        ('s_game_new_player_phone', 'check_adding_player_phone', ('game_new_player_phone')),
        ('s_game_set_won_score', 'check_setting_score', ('game_set_score_won')),
        ('s_game_set_lost_score', 'check_setting_score', ('game_set_score_lost')),
        ('s_nick_adding_player', 'check_adding_player', ('nick_already_exists', 'nick_new_player')),
        ('s_nick_new_player_phone', 'check_adding_player_phone', ('nick_new_player_phone')),
        ('s_players', 'check_player_found', ('players_found', 'players_not_found')),
        ('s_games', 'check_game_found', ('games_found', 'games_not_found'))
    )

    def _check_error_is_fatal(self, err, processing_message):
        if err is not None and err['error_type'] != 'negative response':
            raise RuntimeError(json.dumps(err))

    ''' Checks '''
    # return tuple (index of transition, parsed arguments)
    def check_adding_player(self, user_input, processing_message=None):
        logger.debug('check_adding_player')
        if type(user_input) == Player:
            return (0, user_input)

        err, player = self.backend.get_player(nick=user_input)
        self._check_error_is_fatal(err, processing_message)
        if player is not None:
            return (0, player)
        else:
            return (1, Player(nick=user_input, phone=None))

    def check_player_found(self, user_input, processing_message=None):
        logger.debug('check_player_found')
        if type(user_input) == Player:
            user_input = user_input.nick

        err, player = self.backend.get_player(nick=user_input)
        self._check_error_is_fatal(err, processing_message)
        if player is not None:
            return (0, player)
        else:
            return (1, None)

    def check_game_found(self, user_input, processing_message=None):
        logger.debug('check_game_found')
        if type(user_input) == Player:
            user_input = user_input.nick

        err, games = self.backend.get_games(nick=user_input)
        self._check_error_is_fatal(err, processing_message)
        if games is not None and len(games) > 0:
            return (0, games)
        else:
            return (1, None)

    def check_adding_player_phone(self, user_input, processing_message=None):
        logger.debug('check_adding_player_phone')
        try:
            phone = int(self._normalize_phone(user_input))
            return (0, str(phone))
        except ValueError:
            self.show_message(
                message=self.text.phone_incorrect(),
                processing_message=processing_message,
                reply=True
            )
            return (-1, None)

    def check_setting_score(self, user_input, processing_message=None):
        logger.debug('check_setting_score')
        try:
            score = int(user_input)
            if score >= 0:
                if self.state.is_s_game_set_lost_score or score > 14:
                    if self.state.is_s_game_set_lost_score and score + 1 >= self._game.score_won:
                        self.show_message(
                            message=self.text.check_score_looser_less_than_winner(),
                            processing_message=processing_message,
                            reply=True
                        )
                        return (-1, None)
                    return (0, score)
                else:
                    self.show_message(
                        message=self.text.check_score_winner_min_value(),
                        processing_message=processing_message,
                        reply=True
                    )
                    return (-1, None)
            else:
                self.show_message(
                    message=self.text.check_score_min_value(),
                    processing_message=processing_message,
                    reply=True
                )
                return (-1, None)
        except ValueError:
            self.show_message(
                message=self.text.check_score_is_not_a_number(),
                processing_message=processing_message,
                reply=True
            )
            return (-1, None)

    ''' Transitions '''
    @xworkflows.transition()
    def goto_init(self, user_input=None, processing_message=None, message=None):
        logger.debug('goto_init')
        self.show_message(
            message=message,
            buttons=['/game', '/players', '/games', '/cancel'],
            keyboard=True,
            processing_message=processing_message
        )

    @xworkflows.transition()
    def game_add(self, user_input=None, processing_message=None):
        logger.debug('game_add')
        self._game = Game()
        self.show_message(
            message=self.text.game(),
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
            message=self.text.game_add_new_player(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def game_new_player_phone(self, phone, processing_message=None):
        logger.debug('game_new_player_phone')
        self._player.phone = self._normalize_phone(phone)
        err, self._player = self.backend.add_player(player=self._player, who=processing_message.ids.user_id)
        self._check_error_is_fatal(err, processing_message)

    @xworkflows.transition()
    def game_set_score_won(self, score, processing_message=None):
        logger.debug('game_set_score_won')
        self._game.score_won = score
        self.show_message(
            message=self.text.game_score_winner_set_next_looser(),
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
            message=self.text.game_score_set_winner(),
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
        self._check_error_is_fatal(err, processing_message)
        self._game = g
        self.show_message(
            message=self.text.game_saved(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def nick(self, user_input=None, processing_message=None):
        logger.debug('nick')
        self.show_message(
            message=self.text.nick(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def nick_already_exists(self, arg=None, processing_message=None):
        logger.debug('nick_already_exists')
        self.show_message(
            message=self.text.nick_already_exists(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def nick_new_player(self, player, processing_message=None):
        logger.debug('nick_new_player')
        self._player = player
        self.show_message(
            message=self.text.nick_adding_enter_phone(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def nick_new_player_phone(self, phone, processing_message=None):
        logger.debug('nick_new_player_phone')
        self._player.phone = self._normalize_phone(phone)
        err, self._player = self.backend.add_player(player=self._player, who=processing_message.ids.user_id)
        self._check_error_is_fatal(err, processing_message)
        self.show_message(
            message=self.text.nick_added(self._player),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def players_wait(self, processing_message=None):
        logger.debug('players_wait')
        self.show_message(
            message=self.text.players(),
            buttons=[Button(
                text='search',
                switch_inline='/players ',
                callback=None
            )],
            processing_message=processing_message
        )

    @xworkflows.transition()
    def players_found(self, player, processing_message=None):
        logger.debug('players_found')
        self.show_message(
            message=self.text.players_found(player),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def players_not_found(self, player, processing_message=None):
        logger.debug('players_not_found')
        self.show_message(
            message=self.text.players_not_found(),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def games_wait(self, processing_message=None):
        logger.debug('games_wait')

    @xworkflows.transition()
    def games_found(self, games, processing_message=None):
        logger.debug('games_found')
        self.show_message(
            message=self.text.games_found(games, len(games)),
            processing_message=processing_message
        )

    @xworkflows.transition()
    def games_not_found(self, game, processing_message=None):
        logger.debug('games_not_found')
        self.show_message(
            message=self.text.games_not_found(),
            processing_message=processing_message
        )

    @xworkflows.on_enter_state('s_game_player_confirmed')
    def _on_s_game_player_confirmed(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_game_player_confirmed')
        self._add_player_to_game()
        self.show_message(
            message=self.text.game_player_added(),
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
                switch_inline='/players ',
                callback=None
            )],
            processing_message=processing_message
        )

    @xworkflows.on_enter_state('s_game_created')
    def _on_s_game_created(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_game_created')
        self.game_save(processing_message)

    @xworkflows.on_enter_state('s_players')
    def _on_s_players(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_players')

    @xworkflows.on_enter_state('s_games')
    def _on_s_players(self, transition_res=None, transition_arg=None, processing_message=None):
        logger.debug('_on_s_games')
        self.show_message(
            message=self.text.games(),
            buttons=[Button(
                text='search',
                switch_inline='/players ',
                callback=None
            )],
            processing_message=processing_message
        )

    def game(self, user_input=None, processing_message=None):
        logger.debug('players')
        if user_input is None or len(user_input) == 0 and self.state.is_init:
            return self.game_add(processing_message=processing_message)

        if user_input is not None:
            params = user_input.split(';')
            nicks_won = params[0:2]
            nicks_lost = params[2:4]
            score_won = params[4]
            score_lost = params[5]
            self._game = Game(nicks_won=nicks_won, nicks_lost=nicks_lost,
                score_won=score_won, score_lost=score_lost)

            for nick in params[0:3]:
                err, p = self.backend.get_player(nick=nick)
                self._check_error_is_fatal(err, processing_message)
                if err is not None:
                    return self.goto_init(
                        message=self.text.nick_not_exists() + '\n' + self.text.cancel(),
                        processing_message=processing_message
                    )
                self._game.set_rating_before(nick=nick, rating=p.get_rating())

            err, g = self.backend.add_game(game=self._game, who=processing_message.ids.user_id)
            self._check_error_is_fatal(err, processing_message)
            if err is not None:
                return self.goto_init(
                    message=self.text.game_save_fail(err),
                    processing_message=processing_message
                )

            self._game = g
            self.show_message(
                message=self.text.game_saved(),
                processing_message=processing_message
            )


    def players(self, user_input=None, processing_message=None):
        logger.debug('players')
        if user_input is None or len(user_input) == 0 and self.state.is_init:
            return self.players_wait(processing_message=processing_message)

        if user_input is not None:
            user_input = user_input.strip()
        if user_input is not None and len(user_input) > 2:
            err, players = self.backend.get_players(nick_like=user_input)
            self._check_error_is_fatal(err, processing_message)
            self.show_contacts(
                contacts=players,
                processing_message=processing_message
            )

    def games(self, user_input=None, processing_message=None):
        logger.debug('games')
        if user_input is None or len(user_input) == 0 and self.state.is_init:
            return self.games_wait(processing_message=processing_message)

        if user_input is not None:
            user_input = user_input.strip()
        if user_input is not None and len(user_input) > 2:
            err, games = self.backend.get_games(nick=user_input)
            self._check_error_is_fatal(err, processing_message)
            self.show_message(
                message=json.dumps(games),
                processing_message=processing_message
            )

    def start(self, user_input=None, processing_message=None):
        logger.debug('start')
        self.goto_init(message=self.text.start(), processing_message=processing_message)

    def cancel(self, user_input=None, processing_message=None):
        logger.debug('cancel')
        self.goto_init(message=self.text.cancel(), processing_message=processing_message)

    def help(self, user_input=None, processing_message=None):
        logger.debug('help')
        self.show_message(
            message=self.text.help(),
            processing_message=processing_message
        )

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
