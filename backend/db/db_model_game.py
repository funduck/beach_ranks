from db import db
import datetime

class Game(object):
	def __init__(self, id=None, date=None, team_won=None, team_lost=None, score_won=None, score_lost=None, status='ok'):
		self.id = id
		self.date = date
		self.team_won = team_won # array of players ids in team that won
		self.team_lost = team_lost # array of players ids in team that lost
		self.score_won = score_won
		self.score_lost = score_lost
		self.status = status

	def sql_save_game(self):
		# table Games is (game_id number, status varchar, date date, score_won number, score_lost number)
		return ['select * from beach_ranks.save_game(%s, %s, %s, %s, %s);',
			[self.id, self.status, self.date.isoformat(), self.score_won, self.score_lost]
			]

	def sql_save_teams(self):
		# table Game_players is (game_id integer, player_id integer, win boolean, valid boolean)
		sqls = ''
		params = []
		for p in self.team_won:
			sqls += 'select * from beach_ranks.save_game_player(%s, %s, %s, %s);'
			params.extend([self.id, p, True, True])

		for p in self.team_lost:
			sqls += 'select * from beach_ranks.save_game_player(%s, %s, %s, %s);'
			params.extend([self.id, p, False, True])

		return [sqls, params]

	def sql_delete_game(self):
		return ['delete from beach_ranks.games where game_id = %s;'\
			'delete from beach_ranks.game_players where game_id = %s', [self.id, self.id]
			]

	def sql_load_game(self):
		return ['select status, to_char(date, \'yyyy-mm-dd hh24:mi:ss\'), score_won, score_lost '\
			'from beach_ranks.games where game_id = %s', [self.id]
			]

	def sql_load_game_players(self):
		return ['select player_id, win from beach_ranks.game_players where game_id = %s and valid = True', [self.id]]

	async def save(self):
		res = await db.execute(self.sql_save_game())
		self.id = res[0][0]
		await db.execute(self.sql_save_teams())

	async def delete(self):
		await db.execute(self.sql_delete_game())

	async def load(self):
		res = await db.execute(self.sql_load_game())
		res = res[0]
		self.status = res[0]
		self.date = datetime.datetime.strptime(res[1], '%Y-%m-%d %H:%M:%S')
		self.score_won = res[2]
		self.score_lost = res[3]
		res = await db.execute(self.sql_load_game_players())
		self.team_won = []
		self.team_lost = []
		for player in res:
			if player[1] == True:
				self.team_won.append(player[0])
			else:
				self.team_lost.append(player[0])