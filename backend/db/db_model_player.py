from .db import db


class Player(object):
    def __init__(self, id=0, nick=None, phone=None):
        self.id = id
        self.nick = nick
        self.phone = phone
        self.rating = {}

    def get_rating(self, rating_code):
        if self.rating[rating_code] is None:
            return None
        return [self.rating[rating_code]["value"], self.rating[rating_code]["accuracy"]]

    def set_rating(self, rating_code, rating):
        self.rating[rating_code] = {'value': rating[0], 'accuracy': rating[1]}

    def sql_save_player(self, who):
        # table Players is (player_id number, nick varchar, phone varchar)
        sql = 'select * from beach_ranks.save_player(%s, %s, %s, %s);' 
        params = [self.id, self.nick, self.phone, who]

        return [sql, params]

    def sql_delete_completely_player(self):
        return ['delete from beach_ranks.players where player_id = %s;'\
            'delete from beach_ranks.ratings where player_id = %s;', [self.id, self.id]
            ]

    def sql_save_rating(self, who):
        # table Ratings is (rating_id varchar, player_id number, rating_code varchar, value number, accuracy number)
        sql = ''
        params = []
        for r_code in self.rating:
            rating = self.rating[r_code]
            sql += 'select * from beach_ranks.save_rating(%s, %s, %s, %s, %s);'
            params.extend([self.id, r_code, rating['value'], rating['accuracy'], who])
    
        return [sql, params]

    def sql_ratings(self):
        return ['select r.rating_code, value, accuracy, descr from beach_ranks.ratings r, beach_ranks.ratings_defs d '
                'where player_id = %s and r.rating_code = d.rating_code', [self.id]]

    def sql_load_player(self):
        if self.id is not None and self.id > 0:
            return ['select player_id, nick, phone from beach_ranks.players where player_id = %s', [self.id]]
        if self.phone is not None:
            return ['select player_id, nick, phone from beach_ranks.players where phone = %s', [self.phone]]

    async def save(self, who='test'):
        res = await db.execute(self.sql_save_player(who))
        self.id = res[0][0]
        await db.execute(self.sql_save_rating(who))

    async def delete_completely(self):
        await db.execute(self.sql_delete_completely_player())

    async def load(self):
        res = await db.execute(self.sql_load_player())
        # TODO check, it returns one record
        res = res[0]
        self.id = res[0]
        self.nick = res[1]
        self.phone = res[2]
        res = await db.execute(self.sql_ratings())
        for rating in res:
            self.rating[rating[0]] = {'value': rating[1], 'accuracy': rating[2]} 