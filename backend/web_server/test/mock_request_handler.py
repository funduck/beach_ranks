import typing

from web_server import RequestHandler


class MockRequestHandler(RequestHandler):
    def __init__(self):
        super().__init__()

    async def handle_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_nick(self, args: typing.Dict):
        return f'/nick?{args}'

    async def post_forget(self, args: typing.Dict):
        return f'/forget?{args}'

    async def post_game(self, args: typing.Dict):
        return f'/game?{args}'

    async def handle_list(self, args: typing.Dict):
        return f'/list?{args}'

    async def handle_help(self, args: typing.Dict):
        return f'/help?{args}'
