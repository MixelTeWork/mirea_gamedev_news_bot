import bafser_tgapi as tgapi

from bot.bot import Bot
from bot.utils import silent_mode
from data.broadcast import Broadcast


@Bot.add_command(desc_adm=("Новости будут транслироваться в данный чат", "[\\s]"))
@Bot.cmd_for_admin
def set_news_chat(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.message:
        return
    s = silent_mode(bot, args)
    added = Broadcast.add_by_message(bot.message)

    if not s:
        if added:
            return "⚙ В этот чат будут транслироваться новости"
        return "⚙ В этот чат уже транслируются новости"


@Bot.add_command(desc_adm=("Новости больше не будут транслироваться в данный чат", "[\\s]"))
@Bot.cmd_for_admin
def unset_news_chat(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.message:
        return
    s = silent_mode(bot, args)
    bc = Broadcast.get_by_message(bot.message)
    if bc:
        bc.delete()

    if not s:
        if bc:
            return "⚙ В этот чат больше не будут транслироваться новости"
        return "⚙ В этот чат не транслируются новости"


@Bot.on_my_chat_member
def on_my_chat_member(bot: Bot):
    assert bot.my_chat_member
    if bot.my_chat_member.chat.type != "channel":
        return

    if bot.my_chat_member.new_chat_member.status == "administrator":
        added = Broadcast.add_by_chat(bot.my_chat_member.chat)

        if added:
            txt = "⚙ В этот канал будут транслироваться новости"
        else:
            txt = "⚙ В этот канал уже транслируются новости"
        bot.sendMessage(txt)
    else:
        bc = Broadcast.get_by_chat(bot.my_chat_member.chat.id, None)
        if bc:
            bc.delete()
