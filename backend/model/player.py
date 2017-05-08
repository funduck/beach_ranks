from collections import namedtuple

Rating = namedtuple('Rating', ['value', 'accuracy'])


class Player:
    def __init__(self, player_id=None, nick=None, rating=None, user_id=None, phone=None):
        self.id = player_id
        self.nick = nick
        self.rating = {} if rating is None else rating
        self.user_id = user_id
        self.phone = phone

    def set_rating(self, rating: Rating):
        self.rating['trueskill'] = rating

    def get_rating(self):
        if 'trueskill' not in self.rating:
            return None

        return self.rating['trueskill']