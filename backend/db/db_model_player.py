from db import DB
import asyncio

def db_str(s):
	return '\'' + s + '\''

class Player(object):
	def __init__(self):
		self.id = 0
		self.nick = 'nick'
		self.phone = '79161234567'
		self.rating = {'trueskill': {'value': 0, 'accuracy': 0}}
		self.status = 'active'

	def get_true_skill(self):
		return {
			'mu': self.rating['trueskill']['value'],
			'sigma': self.rating['trueskill']['accuracy']
		}

	def set_true_skill(self, mu, sigma):
		self.rating['trueskill'] = {'value': mu, 'accuracy': sigma}

	def sql_save_player(self):
		# table Players is (player_id number, status varchar, nick varchar, phone varchar)
		sql = 'select * from beach_ranks.save_player(%s, %s, %s, %s);' 
		params = [self.id, db_str(self.status), db_str(self.nick), db_str(self.phone)]

		return [sql, params]

	def sql_save_rating(self):
		# table Ratings is (rating_id varchar, player_id number, value number, accuracy number)
		sql = ''
		params = []
		for r_code in self.rating:
			rating = self.rating[r_code]
			sql += 'select * from beach_ranks.save_rating(%s, %s, %s, %s);'
			params.extend([r_code, self.id, rating['value'], rating['accuracy']])
	
		return [sql, params]

	def sql_ratings(self):
		return ['select d.code, value, accuracy, descr from beach_ranks.ratings r, beach_ranks.ratings_defs d '\
		'where player_id = %s and r.rating_id = d.rating_id', [self.id]]

	def set_db(self, db):
		self.db = db

	async def save(self):
		res = await self.db.execute(self.sql_save_player())
		self.id = res[0][0]
		await self.db.execute(self.sql_save_rating())