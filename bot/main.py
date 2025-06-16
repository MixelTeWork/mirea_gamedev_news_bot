from bot.bot import Bot
import tgapi

bot = Bot()


def setup_bot():
    bot.init()


def process_update(update: tgapi.Update):
    bot.process_update(update)
