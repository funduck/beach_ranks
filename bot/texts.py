import json

class Texts():
    def __init__(self, locale='en'):
        self.locale = locale

    def check_phone_incorrect(self):
        if self.locale == 'en':
            return 'Phone number is incorrect'
        if self.locale == 'ru':
            return 'Что-то не так в этом номере'

    def check_score_looser_less_than_winner(self):
        if self.locale == 'en':
            return 'Score of a looser +1 should be < score of a winner'
        if self.locale == 'ru':
            return 'Очков у проигравшего должно быть меньше чем у победителя не меньше чем на 2'

    def check_score_winner_min_value(self):
        if self.locale == 'en':
            return 'Score of a winner should be >= 15'
        if self.locale == 'ru':
            return 'У победителя не может быть меньше 15 очков'

    def check_score_min_value(self):
        if self.locale == 'en':
            return 'Score should be >= 0'
        if self.locale == 'ru':
            return 'Очков меньше 0 ну точно не может быть :)'

    def check_score_is_not_a_number(self):
        if self.locale == 'en':
            return 'Score is not a number'
        if self.locale == 'ru':
            return 'Должно быть число'

    def start(self):
        if self.locale == 'en':
            return 'Hello, I do trueskill ranking for games 2x2\nnow you are in start menu'
        if self.locale == 'ru':
            return 'Привет, я рейтингую игры 2х2 по системе trueskill\nсейчас ты в стартовом меню'

    def cancel(self):
        if self.locale == 'en':
            return 'Canceled\nnow you are in start menu'
        if self.locale == 'ru':
            return 'Отменено\nсейчас ты в стартовом меню'

    def help(self):
        if self.locale == 'en':
            return 'Oh.. Dunno, it\'s nothing here'
        if self.locale == 'ru':
            return 'Э.. я хз, тут ничего нет :)'

    def game(self):
        if self.locale == 'en':
            return 'Adding game'  # \n1) enter players, won team, then lost\n2) enter scores, won first'
        if self.locale == 'ru':
            return 'Добавляем игру'  # ' так:\n1) записываем игроков, сначала выигравшую команду\n2) вводим счет, тоже начиная с победителя'

    def game_add_next_player(self, game):
        if self.locale == 'en':
            if len(game.nicks_won) < 2:
                team = 'winner'
                player = len(game.nicks_won) + 1
            else:
                team = 'looser'
                player = len(game.nicks_lost) + 1
            return f'Team \'{team}\' enter {player} player\'s name'
        if self.locale == 'ru':
            if len(game.nicks_won) < 2:
                team = 'победитель'
                player = len(game.nicks_won) + 1
            else:
                team = 'проигравший'
                player = len(game.nicks_lost) + 1
            return f'Команда \'{team}\' добавь {player}-го игрока'

    def game_add_new_player(self):
        if self.locale == 'en':
            return 'Someone new, enter his phone number'
        if self.locale == 'ru':
            return 'Кто-то новенький, какой у него телефон?'

    def game_player_added(self):
        if self.locale == 'en':
            return 'Player added'
        if self.locale == 'ru':
            return 'Игрок добавлен'

    def game_score_set_winner(self):
        if self.locale == 'en':
            return 'Score of a winner?'
        if self.locale == 'ru':
            return 'Сколько очков у победителя?'

    def game_score_winner_set_next_looser(self):
        if self.locale == 'en':
            return 'Now score of a looser'
        if self.locale == 'ru':
            return 'А у проигравших?'

    def game_score_set_done(self):
        if self.locale == 'en':
            return 'Done with scores'
        if self.locale == 'ru':
            return 'Очки записали'

    def game_saved(self):
        if self.locale == 'en':
            return 'Game saved'
        if self.locale == 'ru':
            return 'Игра сохранена'

    def nick(self):
        if self.locale == 'en':
            return 'Adding player, what\'s his name?'
        if self.locale == 'ru':
            return 'Добавляем игрока, как его зовут?'

    def nick_already_exists(self):
        if self.locale == 'en':
            return 'Player with this nick already exists'
        if self.locale == 'ru':
            return 'Игрок с таким именем уже есть'

    def nick_not_exists(self):
        if self.locale == 'en':
            return 'Player with this nick not exists'
        if self.locale == 'ru':
            return 'Игрока с таким именем нет'

    def nick_adding_enter_phone(self):
        if self.locale == 'en':
            return 'What\'s his phone number?'
        if self.locale == 'ru':
            return 'Какой у него телефон?'

    def nick_added(self, player):
        if self.locale == 'en':
            return f'Player \'{player.nick}\' added'
        if self.locale == 'ru':
            return f'Игрок \'{player.nick}\' добавлен'

    def players(self):
        if self.locale == 'en':
            return 'Who are we looking for?'
        if self.locale == 'ru':
            return 'Кого мы ищем'

    def players_found(self, player):
        if self.locale == 'en':
            return f'\'{player.nick}\' rating: {round(player.get_rating()[0], 2)} accuracy: {round(player.get_rating()[1], 2)}'
        if self.locale == 'ru':
            return f'\'{player.nick}\' рейтинг: {round(player.get_rating()[0], 2)} точность: {round(player.get_rating()[1], 2)}'

    def players_not_found(self):
        if self.locale == 'en':
            return 'Couldn\'t find anyone'
        if self.locale == 'ru':
            return 'Никого не нашлось'

    def games(self):
        if self.locale == 'en':
            return 'Who\'s games are we looking for?'
        if self.locale == 'ru':
            return 'Чьи игры мы ищем'

    def games_found(self, games, count):
        s = ''
        for g in games:
            s += f'{g.date} {json.dumps(g.nicks_won)} {g.score_won}:{g.score_lost} {json.dumps(g.nicks_lost)}\n'
        if self.locale == 'en':
            return f'last {count}\n' + s
        if self.locale == 'ru':
            return f'последние {count}\n' + s

    def games_not_found(self):
        if self.locale == 'en':
            return 'Couldn\'t find any'
        if self.locale == 'ru':
            return 'Ничего не нашлось'
