from collections import namedtuple

BeachranksRestServiceConfig = namedtuple('BeachranksRestServiceConfig',
    ['port', 'db_name', 'db_user', 'db_pw', 'db_host', 'db_port'])
BeachranksBotConfig = namedtuple('BeachranksBotConfig',
    ['host', 'port', 'name', 'token', 'locale'])


class ConfigClass:
    def __init__(self):
        self.bot = None
        self.rest_service = None


Config = ConfigClass()


def initConfig(mode):
    if mode is None:
        Config.bot=BeachranksBotConfig(
            host='185.4.74.144',
            port=8443,
            name='beachranks_bot',
            token='bot299909888:AAEjhCS1I55FFrRrLyMiUFpZDH8nu5JZ0Q8',
            locale='ru'
        )
        Config.rest_service=BeachranksRestServiceConfig(
            port=9999,
            db_name='beach_ranks',
            db_user='beach_ranks',
            db_pw='beachranks',
            db_host='localhost',
            db_port=5432
        )
    if mode == 'test':
        Config.bot=BeachranksBotConfig(
            host='185.4.74.144',
            port=8443,
            name='beachranks_bot_test',
            token='bot437824095:AAGQoMisbCY55sw9LT7e24YDso1_LnpyeNw',
            locale='ru'
        )
        Config.rest_service=BeachranksRestServiceConfig(
            port=9998,
            db_name='beach_ranks_test',
            db_user='beach_ranks',
            db_pw='beachranks',
            db_host='localhost',
            db_port=5432
        )
    if mode == 'unittest':
        Config.bot=BeachranksBotConfig(
            host='localhost',
            port=8888,
            name='beachranks_bot_test',
            token='bot437824095:AAGQoMisbCY55sw9LT7e24YDso1_LnpyeNw',
            locale='ru'
        )
        Config.rest_service=BeachranksRestServiceConfig(
            port=9997,
            db_name='beach_ranks_test',
            db_user='beach_ranks',
            db_pw='beachranks',
            db_host='localhost',
            db_port=5432
        )
