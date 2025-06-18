from bot.bot import Bot
from bot.utils import silent_mode
from data.config import Config
import tgapi

ME = tgapi.MessageEntity


@Bot.add_command("set_news_chat", (None, ("Новости будут транслироваться в данный чат", "[\\s]")))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def set_news_chat(bot: Bot, args: tgapi.BotCmdArgs):
    s = silent_mode(bot, args)
    config = Config.get(bot.db_sess)
    config.set_chat(bot.user, bot.message.chat.id, bot.message.message_thread_id)

    if not s:
        return "⚙ В этот чат будут транслироваться новости"
