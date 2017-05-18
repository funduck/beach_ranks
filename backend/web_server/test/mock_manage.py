import typing

from model import Player, Game


class MockManage:
    def __init__(self, players: typing.Dict, games: typing.List[Game]):
        self.players = players
        self.games = games

    async def save_player(self, player: Player):
        self.players[player.nick] = player

    async def delete_player(self, player: Player):
        del self.players[player.nick]

    async def save_game(self, game: Game):
        self.games.append(game)
