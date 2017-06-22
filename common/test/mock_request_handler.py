import typing


class MockRequestHandler:
    def __init__(self):
        super().__init__()

    async def get_home(self, args: typing.Dict):
        return f'/?{args}'

    async def post_nick(self, args: typing.Dict):
        return f'/nick?{args}'

    async def post_forget(self, args: typing.Dict):
        return f'/forget?{args}'

    async def post_game(self, args: typing.Dict):
        return f'/game?{args}'

    async def get_list(self, args: typing.Dict):
        return f'/list?{args}'

    async def get_help(self, args: typing.Dict):
        return f'/help?{args}'
