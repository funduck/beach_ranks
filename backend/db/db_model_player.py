from db import db
import asyncio

class Player(object):
    def __init__(self, id=0, nick=None, phone=None):
        self.id = id
        self.nick = nick
        self.phone = phone
        self.rating = {}
        self.status = 'ok'

    def get_true_skill(self):
        if self.rating['trueskill'] is None:
            return None
        return {
            'mu': self.rating['trueskill']['value'],
            'sigma': self.rating['trueskill']['accuracy']
        }

    def set_true_skill(self, mu, sigma):
        self.rating['trueskill'] = {'value': mu, 'accuracy': sigma}

    def sql_save_player(self):
        # table Players is (player_id number, status varchar, nick varchar, phone varchar)
        sql = 'select * from beach_ranks.save_player(%s, %s, %s, %s);' 
        params = [self.id, self.status, self.nick, self.phone]

        return [sql, params]

    def sql_delete_player(self):
        return ['update beach_ranks.players set status = \'deleted\' and player_id = %s', [self.id]]

    def sql_delete_completely_player(self):
        return ['delete from beach_ranks.players where player_id = %s;'\
            'delete from beach_ranks.ratings where player_id = %s;', [self.id, self.id]
            ]

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
        return ['select rating_code, value, accuracy, descr from beach_ranks.ratings r, beach_ranks.ratings_defs d '\
        'where player_id = %s and r.rating_id = d.rating_id', [self.id]]

    def sql_load_player(self):
        if self.id > 0:
            return ['select player_id, status, nick, phone from beach_ranks.players where player_id = %s', [self.id]]
        if self.phone is not None:
            return ['select player_id, status, nick, phone from beach_ranks.players where phone = %s', [self.phone]]

    async def save(self):
        res = await db.execute(self.sql_save_player())
        self.id = res[0][0]
        res = await db.execute(self.sql_save_rating())

    async def delete_completely(self):
        res = await db.execute(self.sql_delete_completely_player())

    async def delete(self):
        res = await db.execute(self.sql_delete_player())

    async def load(self):
        res = await db.execute(self.sql_load_player())
        # TODO check, it returns one record
        res = res[0]
        self.status = res[1]
        self.nick = res[2]
        self.phone = res[3]
        res = await db.execute(self.sql_ratings())
        for rating in res:
            self.rating[rating[0]] = {'value': rating[1], 'accuracy': rating[2]} 