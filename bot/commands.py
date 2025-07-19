from bot.bot import Bot
from bot.utils import silent_mode
from data.broadcast import Broadcast
import tgapi

ME = tgapi.MessageEntity


@Bot.add_command("set_news_chat", (None, ("Новости будут транслироваться в данный чат", "[\\s]")))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def set_news_chat(bot: Bot, args: tgapi.BotCmdArgs):
    s = silent_mode(bot, args)
    added = Broadcast.add_by_message(bot.user, bot.message)

    if not s:
        if added:
            return "⚙ В этот чат будут транслироваться новости"
        return "⚙ В этот чат уже транслируются новости"


@Bot.add_command("unset_news_chat", (None, ("Новости больше не будут транслироваться в данный чат", "[\\s]")))
@Bot.cmd_connect_db
@Bot.cmd_for_admin
def unset_news_chat(bot: Bot, args: tgapi.BotCmdArgs):
    s = silent_mode(bot, args)
    bc = Broadcast.get_by_message(bot.db_sess, bot.message)
    if bc:
        bc.delete(bot.user)

    if not s:
        if bc:
            return "⚙ В этот чат больше не будут транслироваться новости"
        return "⚙ В этот чат не транслируются новости"
