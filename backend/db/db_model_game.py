def db_str(s):
	return '"' + s + '"'

class Game(object):
	def __init__(self):
		self.id = 0
		self.date = 'hh24:mi:ss dd.mm.yyyy'
		self.team_won = [0, 0] # array of players ids in team that won
		self.team_lost = [0, 0] # array of players ids in team that lost
		self.score_won = 0
		self.score_lost = 0
		self.status = 'new'

	def sql_save_new(self):
		# table Games is (game_id number, status varchar, date date, score_won number, score_lost number)
		sqls = ['insert into beach_ranks.games values '\
			'(' + str(self.id) + ', ' + db_str(self.status) + ', '\
			+ 'to_date(' + db_str(self.date) + ', "hh24:mi:ss dd.mm.yyyy"), '\
			+ str(self.score_won) + ', ' + str(self.score_lost) + ')']

		# table Game_players is (game_id integer, player_id integer, win boolean, valid boolean)
		for p in self.team_won:
			sqls.append('insert into beach_ranks.game_players values '\
				'(' + str(self.id) + ', ' + str(self.team_won[p]) + ', true, true)')

		for p in self.team_lost:
			sqls.append('insert into beach_ranks.game_players values '\
				'(' + str(self.id) + ', ' + str(self.team_lost[p]) + ', false, true)')

		return sqls