from model.player import Rating


class Game:
    def __init__(self, game_id=None, nicks_won=None, nicks_lost=None, ratings=None, score_won=0, score_lost=0):
        self.game_id = game_id
        self.nicks_won = [] if nicks_won is None else nicks_won
        self.nicks_lost = [] if nicks_lost is None else nicks_lost
        self.ratings = {} if ratings is None else ratings
        self.score_won = score_won
        self.score_lost = score_lost

    def set_rating_before(self, nick: str, rating: Rating):
        if nick not in self.nicks_won and nick not in self.nicks_lost:
            raise RuntimeError(f'Invalid nickname given: {nick}')

        self._init_rating(nick)
        self.ratings[nick]['before']['trueskill'] = rating

    def rating_before(self, nick: str):
        if nick not in self.ratings:
            return None

        return self.ratings[nick]['before']

    def set_rating_after(self, nick: str, rating: Rating):
        if nick not in self.nicks_won and nick not in self.nicks_lost:
            raise RuntimeError(f'Invalid nickname given: {nick}')

        self._init_rating(nick)
        self.ratings[nick]['after']['trueskill'] = rating

    def rating_after(self, nick: str):
        if nick not in self.ratings:
            return None

        return self.ratings[nick]['after']

    def _init_rating(self, nick):
        if nick not in self.ratings:
            self.ratings[nick] = {
                'before': {},
                'after': {}
            }
