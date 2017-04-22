import typing
from aiohttp import web


class RequestHandler:
    def __init__(self):
        pass

    def handle_nick(self, args: typing.Dict):
        return web.Response(f'handle_nick: {args}')

    def handle_forget(self, args: typing.Dict):
        return web.Response(f'handle_forget: {args}')

    def handle_game(self, args: typing.Dict):
        return web.Response(f'handle_game: {args}')

    def handle_list(self, args: typing.Dict):
        return web.Response(f'handle_list: {args}')

    def handle_help(self, args: typing.Dict):
        return web.Response(f'handle_help: {args}')

