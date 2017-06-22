import datetime
from .player import Rating


ratingSystem = 'trueskill'


class Game:
    def __init__(self, game_id=0, nicks_won=None, nicks_lost=None, ratings=None, score_won=0, score_lost=0, date=None):
        self.id = game_id
        self.nicks_won = [] if nicks_won is None else nicks_won
        self.nicks_lost = [] if nicks_lost is None else nicks_lost
        self.ratings = {} if ratings is None else ratings
        self.score_won = score_won
        self.score_lost = score_lost
        self.date = date
        if self.date is None:
            self.date = datetime.datetime.now()

    def set_rating_before(self, nick: str, rating: Rating):
        if nick not in self.nicks_won and nick not in self.nicks_lost:
            raise RuntimeError(f'Invalid nickname given: {nick}')

        self._init_rating(nick)
        self.ratings[nick]['before'][ratingSystem] = rating

    def rating_before(self, nick: str) -> Rating:
        if nick not in self.ratings:
            return None

        return self.ratings[nick]['before'][ratingSystem]

    def set_rating_after(self, nick: str, rating: Rating):
        if nick not in self.nicks_won and nick not in self.nicks_lost:
            raise RuntimeError(f'Invalid nickname given: {nick}')

        self._init_rating(nick)
        self.ratings[nick]['after'][ratingSystem] = rating

    def rating_after(self, nick: str) -> Rating:
        if nick not in self.ratings:
            return None

        return self.ratings[nick]['after'][ratingSystem]

    def _init_rating(self, nick):
        if nick not in self.ratings:
            self.ratings[nick] = {
                'before': {},
                'after': {}
            }

    def as_dict(self):
        d = {
            'nicks_won': self.nicks_won,
            'nicks_lost': self.nicks_lost,
            'score_won': self.score_won,
            'score_lost': self.score_lost,
            'ratings': self.ratings,
            'date': self.date.isoformat(timespec='seconds')

        }
        return d

    def __repr__(self):
        return f'Game({self.as_dict()})'


def game_from_dict(d):
    return Game(
        nicks_won=d['nicks_won'],
        nicks_lost=d['nicks_lost'],
        ratings=d['ratings'],
        score_won=d['score_won'],
        score_lost=d['score_lost'],
        date=datetime.datetime.strptime(d['date'], '%Y-%m-%dT%H:%M:%S')
    )
