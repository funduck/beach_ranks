import typing


class RequestHandler:
    def __init__(self):
        pass

    def handle_home(self, args: typing.Dict):
        return f'/?{args}'

    def post_nick(self, args: typing.Dict):
        return f'/nick?{args}'

    def post_forget(self, args: typing.Dict):
        return f'/forget?{args}'

    def post_game(self, args: typing.Dict):
        return f'/game?{args}'

    def handle_list(self, args: typing.Dict):
        return f'/list?{args}'

    def handle_help(self, args: typing.Dict):
        return f'/help?{args}'
