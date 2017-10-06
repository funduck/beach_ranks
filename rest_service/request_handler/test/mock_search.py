import typing

from common.model import Game


class MockSearch:
    def __init__(self, players: typing.Dict, games: typing.List[Game]):
        self._players = players
        self._games = games

    async def load_player_by_nick(self, nick):
        return self._players.get(nick, None)

    async def load_players_nick_like(self, nick):
        return [self._players[p] for p in self._players if p.startswith(nick)]

    async def load_games_by_nicks(self, nick, with_players=None, vs_players=None, count=0, max_game_id=0):
        games_filtered = []
        for game in self._games:
            if nick not in game.nicks_won and nick not in game.nicks_lost:
                games_filtered.append(game)

            if nick in game.nicks_won:
                if with_players is not None:
                    for partner in [n for n in game.nicks_won if n != nick]:
                        if partner not in with_players:
                            games_filtered.append(game)

                if vs_players is not None:
                    for enemy in vs_players:
                        if enemy not in game.nicks_lost:
                            games_filtered.append(game)

            if nick in game.nicks_lost:
                if with_players is not None:
                    for partner in [n for n in game.nicks_lost if n != nick]:
                        if partner not in with_players:
                            games_filtered.append(game)

                if vs_players is not None:
                    for enemy in vs_players:
                        if enemy not in game.nicks_won:
                            games_filtered.append(game)

        return [game for game in self._games if game not in games_filtered]
