from bot.bot import Bot
import tgapi


def silent_mode(bot: Bot, args: tgapi.BotCmdArgs):
    if len(args) == 0 or args[-1] != "\\s":
        return False
    args.args = args.args[:-1]
    if bot.message:
        tgapi.deleteMessage(bot.message.chat.id, bot.message.message_id)
    return True
