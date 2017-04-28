from db import db
from db_model_player import Player
import datetime

class Game(object):
	def __init__(self, id=None, date=None, team_won=None, team_lost=None, score_won=None, score_lost=None):
		self.id = id
		self.date = date
		self.team_won = team_won # array of players in team that won
		self.team_lost = team_lost # array of players in team that lost
		self.score_won = score_won
		self.score_lost = score_lost

	def sql_save_game(self, who):
		# table Games is (game_id number, date date, score_won number, score_lost number)
		return ['select * from beach_ranks.save_game(%s, %s, %s, %s, %s);',
			[self.id, self.date.isoformat(), self.score_won, self.score_lost, who]
			]

	def sql_save_teams(self, who):
		# table Game_players is (game_id integer, player_id integer, win boolean)
		sqls = ''
		params = []
		for p in self.team_won:
			sqls += 'select * from beach_ranks.save_game_player(%s, %s, %s, %s);'
			params.extend([self.id, p.id, True, who])

		for p in self.team_lost:
			sqls += 'select * from beach_ranks.save_game_player(%s, %s, %s, %s);'
			params.extend([self.id, p.id, False, who])

		return [sqls, params]

	def sql_save_rating(self, player_id, rating_code, value_before, value_after, accuracy_before, accuracy_after, who):
		return ['select * from beach_ranks.save_game_rating(%s, %s, %s, %s, %s, %s, %s, %s);',
			[self.id, player_id, rating_code, value_before, value_after, accuracy_before, accuracy_after, who]
			]

	def sql_delete_completely_game(self):
		return ['delete from beach_ranks.games where game_id = %s;'\
			'delete from beach_ranks.game_players where game_id = %s;'\
			'delete from beach_ranks.game_ratings where game_id = %s;', [self.id, self.id, self.id]
			]

	def sql_load_game(self):
		return ['select to_char(date, \'yyyy-mm-dd hh24:mi:ss\'), score_won, score_lost '\
			'from beach_ranks.games where game_id = %s', [self.id]
			]

	def sql_load_game_players(self):
		return ['select player_id, win from beach_ranks.game_players where game_id = %s', [self.id]]

	async def save(self, save_players=False, who='test'):
		if save_players == True:
			for p in self.team_won:
				await p.save(who)
			for p in self.team_lost:
				await p.save(who)

		res = await db.execute(self.sql_save_game(who))
		self.id = res[0][0]
		await db.execute(self.sql_save_teams(who))

	async def save_rating(self, player, rating_code, rating_before, rating_after, who='test'):
		await db.execute(self.sql_save_rating(player.id, rating_code, 
			rating_before[0], rating_after[0], rating_before[1], rating_after[1], who))

	async def delete_completely(self):
		await db.execute(self.sql_delete_completely_game())

	async def load(self):
		res = await db.execute(self.sql_load_game())
		res = res[0]
		self.date = datetime.datetime.strptime(res[0], '%Y-%m-%d %H:%M:%S')
		self.score_won = res[1]
		self.score_lost = res[2]
		res = await db.execute(self.sql_load_game_players())
		self.team_won = []
		self.team_lost = []
		for player in res:
			p = Player(id=player[0])
			await p.load()
			if player[1] == True:
				self.team_won.append(p)
			else:
				self.team_lost.append(p)