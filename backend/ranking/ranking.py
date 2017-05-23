import trueskill
from trueskill import TrueSkill

from model.game import Game
from model.player import Rating


class TrueSkillRanking:
    @classmethod
    def calculate(cls, game: Game):
        env = TrueSkill()
        team_won = {nick: cls.from_model_rating(game.rating_before(nick)) for nick in game.nicks_won}
        team_lost = {nick: cls.from_model_rating(game.rating_before(nick)) for nick in game.nicks_lost}
        rated_rating_groups = env.rate([team_lost, team_won], ranks=[0, 1])
        for team in rated_rating_groups:
            for nick in team:
                game.set_rating_after(nick, cls.to_model_rating(team[nick]))

    @staticmethod
    def from_model_rating(rating: Rating) -> trueskill.Rating:
        return trueskill.Rating(rating.value, rating.accuracy)

    @staticmethod
    def to_model_rating(rating: trueskill.Rating) -> trueskill.Rating:
        return Rating(value=rating.mu, accuracy=rating.sigma)

    @staticmethod
    def initial_rating():
        rating = TrueSkill().create_rating()
        return Rating(value=rating.mu, accuracy=rating.sigma)
