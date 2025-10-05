import bafser_tgapi as tgapi

from data.user import User


class Bot(tgapi.BotWithDB[User]):
    _userCls = User


@Bot.add_command()
def news_bot_version(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    return "ℹ news bot version: 2.0"
