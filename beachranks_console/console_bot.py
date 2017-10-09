import logging
from common import logger
import telegram.ext as tg 
import handlers


log = logger.init_logger('beachranks_console')
updater = tg.Updater(token='447474042:AAHRrgLqblJTdeG3wvbMLn_tXVoHJdEtDxo')

dispatcher = updater.dispatcher
dispatcher.add_handler(tg.CommandHandler('add_player', handlers.add_player, pass_args=True))
dispatcher.add_handler(tg.CommandHandler('remove_player', handlers.remove_player, pass_args=True))
dispatcher.add_handler(tg.CommandHandler('player', handlers.player, pass_args=True))
dispatcher.add_handler(tg.CommandHandler('add_game', handlers.add_game, pass_args=True))
dispatcher.add_handler(tg.CommandHandler('games', handlers.games, pass_args=True))
dispatcher.add_handler(tg.CommandHandler('top', handlers.top, pass_args=True))
updater.start_polling()




