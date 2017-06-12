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

	def game(self):
		if self.locale == 'en':
			return 'Adding game' # \n1) enter players, won team, then lost\n2) enter scores, won first'
		if self.locale == 'ru':
			return 'Добавляем игру' # ' так:\n1) записываем игроков, сначала выигравшую команду\n2) вводим счет, тоже начиная с победителя'

	def game_add_next_player(self, game):
		if self.locale == 'en':
			if len(game.nicks_won) < 2:
				team = 'winner'
				player = len(game.nicks_won) + 1
			else:
				team = 'looser'
				player = len(game.nicks_lost) + 1
			return f'Team \'{team}\'\nenter {player} player\'s name'
		if self.locale == 'ru':
			if len(game.nicks_won) < 2:
				team = 'победитель'
				player = len(game.nicks_won) + 1
			else:
				team = 'проигравший'
				player = len(game.nicks_lost) + 1
			return f'Команда \'{team}\'\nдобавь {player}-го игрока'

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
			return 'Enter score of a winner'
		if self.locale == 'ru':
			return 'Сколько очков у победителя?'

	def game_score_winner_set_next_looser(self):
		if self.locale == 'en':
			return 'Ok, now score of a looser'
		if self.locale == 'ru':
			return 'А у проигравших?'

	def game_score_set_done(self):
		if self.locale == 'en':
			return 'Ok, done with scores'
		if self.locale == 'ru':
			return 'Ок, очки записали'

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

	def nick_adding_enter_phone(self):
		if self.locale == 'en':
			return 'What\'s his phone number?'
		if self.locale == 'ru':
			return 'Какой у него телефон?'

	def nick_added(self):
		if self.locale == 'en':
			return 'Player added'
		if self.locale == 'ru':
			return 'Игрок добавлен'
