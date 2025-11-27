from functools import wraps
from typing import Type, override

import bafser_tgapi as tgapi
from bafser import get_app_config

import bafser_config
from data.user import User


class Bot(tgapi.BotWithDB[User]):
    _userCls = User
    _quest_cmds: list[str] = []
    _quest_room_id: str = ""

    @override
    @classmethod
    def init(cls):
        super().init()
        data = tgapi.utils.read_config(bafser_config.config_dev_path if get_app_config().DEV_MODE else bafser_config.config_path)
        cls._quest_room_id = data["quest_room"] if "quest_room" in data else ""
        tgapi.call_async(lambda: tgapi.setMyCommands(
            [tgapi.BotCommand(command=cmd, description=cmd) for cmd in cls._quest_cmds],
            tgapi.BotCommandScope.chat_administrators(cls._quest_room_id))
        )

    @classmethod
    def cmd_for_quest(cls: "Type[Bot]", fn: "Bot.tcmd_fn[Bot]"):
        cls._quest_cmds.append(fn.__name__)

        @wraps(fn)
        def wrapped(bot: "Bot", args: tgapi.BotCmdArgs, **kwargs: str):
            if not bot.chat or str(bot.chat.id) != cls._quest_room_id:
                return "403! You are not in the quest room!"
            return fn(bot, args, **kwargs)
        return wrapped


@Bot.add_command()
def news_bot_version(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    return "ℹ news bot version: 3.1"
