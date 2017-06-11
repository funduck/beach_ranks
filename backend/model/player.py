from collections import namedtuple

Rating = namedtuple('Rating', ['value', 'accuracy'])


class Player:
    def __init__(self, player_id=0, nick=None, rating=None, user_id=None, phone=None):
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

    def equal(self, other):
        return self.id == other.id \
               and self.nick == other.nick \
               and self.user_id == other.user_id \
               and self.phone == other.phone

    def as_dict(self):
        return {
            'nick': self.nick,
            'rating': self.rating,
            'user_id': self.user_id,
            'phone': self.phone
        }

    def __repr__(self):
        return f'Player({self.as_dict()})'


def player_from_dict(d):
    return Player(
        nick=d['nick'],
        rating=d['rating'],
        user_id=d['user_id'],
        phone=d['phone']
    )
