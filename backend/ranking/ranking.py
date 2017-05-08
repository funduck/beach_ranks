from typing import List

import trueskill

from model.game import Game
from model.player import Rating


class TrueSkillRanking:
    @staticmethod
    def calculate(game: Game):
        pass

    @staticmethod
    def initial_rating():
        return Rating(value=0, accuracy=0)
