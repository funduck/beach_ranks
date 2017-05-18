import typing

from model import Player, Game


class MockSearch:
    def __init__(self, players: typing.Dict, games: typing.List[Game]):
        self._players = players
        self._games = games

    async def load_player_by_nick(self, nick):
        return self._players.get(nick, None)

    async def games(self, nick, with_players=None, vs_players=None):
        games_found = []
        for game in self._games:
            if nick not in game.nicks_won and nick not in game.nicks_lost:
                continue

            if nick in game.nicks_won:
                if with_players is not None:
                    for partner in [n for n in game.nicks_won if n != nick]:
                        if partner not in with_players:
                            continue

                if vs_players is not None:
                    for enemy in game.nicks_lost:
                        if enemy not in vs_players:
                            continue
            if nick in game.nicks_lost:
                if with_players is not None:
                    for partner in [n for n in game.nicks_lost if n != nick]:
                        if partner not in with_players:
                            continue

                if vs_players is not None:
                    for enemy in game.nicks_won:
                        if enemy not in vs_players:
                            continue
            games_found.append(game)

        return games_found
