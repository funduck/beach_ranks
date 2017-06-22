import typing

from common.model import Player, Game


class MockManage:
    def __init__(self, players: typing.Dict, games: typing.List[Game]):
        self._players = players
        self._games = games

    async def save_player(self, player: Player):
        self._players[player.nick] = player

    async def delete_player(self, player: Player):
        del self._players[player.nick]

    async def save_game(self, game: Game):
        self._games.append(game)
