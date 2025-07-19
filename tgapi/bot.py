import re
from typing import Callable, Tuple, Union

from bafser import ParametrizedLogger, add_file_logger
from tgapi import get_bot_name
from .types import *
from .methods import *

cmd_fn = Callable[["Bot", "BotCmdArgs"], Union[None, str]]
cmd_dsc = Union[None, str, Tuple[str, str]]


class Bot:
    update: Update = None
    message: Message = None
    callback_query: CallbackQuery = None
    inline_query: InlineQuery = None
    chosen_inline_result: ChosenInlineResult = None
    my_chat_member: ChatMemberUpdated = None

    _commands: dict[str, Tuple[cmd_fn, Tuple[cmd_dsc, cmd_dsc]]] = {}
    _on: dict[Callable, list[Callable[["Bot"], None]]] = {}
    _sender: Union[User, None] = None
    chat: Union[Chat, None] = None
    TextWrongCommand = "Wrong command"
    logger: "BotLogger" = None

    @property
    def is_callback(self):
        return self.callback_query is not None

    @property
    def sender(self):
        return self._sender

    @sender.setter
    def sender(self, value):
        self._sender = value
        self.logger.user = value

    def init(self):
        fmt = "%(asctime)s;%(levelname)s;%(module)s;%(uid)-10s;%(uname)-15s;%(cmd)-15s;%(message)s"
        self.logger = BotLogger(add_file_logger("logs/bot.csv", "bot", fmt, ["uid", "uname", "cmd"]))
        get_cmd = lambda v: v if isinstance(v, str) else v[0]
        get_dsc = lambda key, i: self._commands[key][1][i]
        replace_vars = lambda cmd: cmd.replace("<", "").replace(">", "")
        setMyCommands([BotCommand(replace_vars(cmd), get_cmd(get_dsc(cmd, 0))) for cmd in self._commands.keys() if get_dsc(cmd, 0)])
        setMyCommands([BotCommand(replace_vars(cmd), get_cmd(get_dsc(cmd, 1) or get_dsc(cmd, 0))) for cmd in self._commands.keys()
                       if get_dsc(cmd, 0) or get_dsc(cmd, 1)], BotCommandScope.all_chat_administrators())

    def get_my_commands(self, admin_only=False):
        pub_keys = [key for key in self._commands.keys() if self._commands[key][1][0]]
        prv_keys = [key for key in self._commands.keys() if self._commands[key][1][1]]
        if admin_only:
            keys = prv_keys
            i = 1
            for key in pub_keys:
                if key in keys:
                    keys.remove(key)
        else:
            keys = pub_keys
            i = 0
        return [(cmd, self._commands[cmd][1][i]) for cmd in keys]

    @classmethod
    def add_command(cls, command: str, description: Union[cmd_dsc, Tuple[cmd_dsc, cmd_dsc]]):
        def wrapper(fn: cmd_fn):
            if isinstance(description, tuple):
                pub, pri = description
            else:
                pub, pri = description, description
                if pri is None:
                    pri = pub

            if "<" in command:
                parts = []
                param = None
                for ch in command:
                    if ch == "<":
                        param = ""
                    elif ch == ">":
                        parts.append((param, True))
                        param = None
                    elif param is not None:
                        param += ch
                    else:
                        if not parts or parts[-1][1]:
                            parts.append(("", False))
                        parts[-1] = (parts[-1][0] + ch, False)
                res = ""
                varnames = []
                for part, isvar in parts:
                    if isvar:
                        res += "(.*)"
                        varnames.append(part)
                    else:
                        res += part
                reg = re.compile(res, re.IGNORECASE)
                fn.regex = reg

                def comparer(cmd: str):
                    m = fn.regex.match(cmd)
                    if not m or len(m.groups()) != len(varnames):
                        return None
                    return dict(zip(varnames, m.groups()))
                fn.comparer = comparer

            cls._commands[command] = (fn, (pub, pri))
            return fn
        return wrapper

    @classmethod
    def on(cls, event: Callable):
        def wrapper(fn: cmd_fn):
            if event not in cls._on:
                cls._on[event] = []
            cls._on[event].append(fn)
            return fn
        return wrapper

    @staticmethod
    def cmd_for_admin(fn):
        def wrapped(bot: Bot, args: BotCmdArgs, **kwargs):
            if bot.chat is None or bot.sender is None:
                return "403(500!)"
            if bot.chat.type != "private":
                ok, r = getChatMember(bot.chat.id, bot.sender.id)
                if not ok:
                    return "403(500)"
                if r.status != "creator" and r.status != "administrator":
                    return "Эта команда только для админов"
            return fn(bot, args, **kwargs)
        return wrapped

    def process_update(self, update: Update):
        self.update = update
        self.message = update.message
        self.callback_query = update.callback_query
        self.inline_query = update.inline_query
        self.chosen_inline_result = update.chosen_inline_result
        self.my_chat_member = update.my_chat_member
        self.sender = None
        self.chat = None
        self.logger._reset()
        if update.message and update.message.text != "":
            self.sender = self.message.sender
            self.chat = self.message.chat
            self.on_message()
            self._call_on(Bot.on_message)
        if update.callback_query:
            self.sender = self.callback_query.sender
            self.chat = self.callback_query.message.chat
            self.on_callback_query()
            self._call_on(Bot.on_callback_query)
        if update.inline_query:
            self.sender = self.inline_query.sender
            self.on_inline_query()
            self._call_on(Bot.on_inline_query)
        if update.chosen_inline_result:
            self.sender = self.chosen_inline_result.sender
            self.on_chosen_inline_result()
            self._call_on(Bot.on_chosen_inline_result)
        if update.my_chat_member:
            self.sender = self.my_chat_member.sender
            self.chat = self.my_chat_member.chat
            self.on_my_chat_member()
            self._call_on(Bot.on_my_chat_member)

    def _call_on(self, event: Callable):
        if event in self._on:
            for fn in self._on[event]:
                fn(self)

    def on_message_text(self):
        pass

    def on_message(self):
        if self.message.text.startswith("/"):
            r = self.on_command(self.message.text[1:])
            if r:
                if isinstance(r, str):
                    self.sendMessage(r)
            # elif r is False:
            #     self.sendMessage(self.TextWrongCommand)
        else:
            self.on_message_text()

    def on_command(self, input: str):
        args = BotCmdArgs(input)
        if args.command == "":
            return False
        cmd, kwargs = self._find_command(args.command)
        if not cmd:
            return False
        fn, description = cmd
        self.logger.cmd = args.command
        r = fn(self, args, **kwargs)
        if r:
            return r
        return True

    def _find_command(self, cmd: str):
        c = self._commands.get(cmd, None)
        if c:
            return c, {}
        for c in self._commands.values():
            if hasattr(c[0], "comparer"):
                kwargs = c[0].comparer(cmd)
                if kwargs:
                    return c, kwargs
        return None, {}

    def on_callback_query(self):
        r = self.on_command(self.callback_query.data)
        if r:
            self.answerCallbackQuery(r if isinstance(r, str) else None)
        else:
            self.answerCallbackQuery(self.TextWrongCommand)

    def on_inline_query(self):
        self.answerInlineQuery([])

    def sendMessage(self, text: str, message_thread_id: int = None, use_markdown=False,
                    reply_markup: InlineKeyboardMarkup = None, reply_parameters: ReplyParameters = None,
                    entities: list[MessageEntity] = None):
        if self.chat is None:
            raise Exception("tgapi: cant send message without chat id")
        chat_id = self.chat.id
        if message_thread_id is None:
            if self.message and self.message.is_topic_message:
                message_thread_id = self.message.message_thread_id
            elif self.callback_query:
                message_thread_id = self.callback_query.message.message_thread_id
        return sendMessage(chat_id, text, message_thread_id, use_markdown, reply_markup, reply_parameters, entities)

    def answerCallbackQuery(self, text: str = None, show_alert: bool = False, url: str = None, cache_time: int = 0):
        if self.callback_query is None:
            raise Exception("tgapi: Bot.answerCallbackQuery is avaible only inside on_callback_query")
        return answerCallbackQuery(self.callback_query.id, text, show_alert, url, cache_time)

    def answerInlineQuery(self, results: list[InlineQueryResult], cache_time: int = 300, is_personal: bool = False, next_offset: str = None):
        if self.callback_query is None:
            raise Exception("tgapi: Bot.answerInlineQuery is avaible only inside on_inline_query")
        return answerInlineQuery(self.inline_query.id, results, cache_time, is_personal, next_offset)

    def on_chosen_inline_result(self):
        pass

    def on_my_chat_member(self):
        pass


class BotLogger(ParametrizedLogger):
    user: User = None
    cmd = ""

    def _reset(self):
        self.user = None
        self.cmd = ""

    def _get_args(self):
        return {
            "uid": self.user.id if self.user else -1,
            "uname": self.user.username if self.user else "",
            "cmd": self.cmd
        }


class BotCmdArgs:
    input: str
    args: list[str]
    raw_args = ""
    raw_argsI = -1
    command = ""

    def __init__(self, input: str):
        self.input = input
        self.args = [str.strip(v) for v in input.split()]

        if len(self.args) == 0:
            return

        command = self.args[0]
        mention = command.find("@")
        if mention > 0:
            bot_name = command[mention:]
            if bot_name != get_bot_name():
                return
            command = command[:mention]
        self.command = command

        self.args = self.args[1:]

        i = input.find(" ")
        if i > 0:
            while i < len(input) and input[i] == " ":
                i += 1
            self.raw_argsI = MessageEntity.len(input[:i])
            self.raw_args = input[i:]

    def __getitem__(self, i: int):
        return self.args[i]

    def __len__(self):
        return len(self.args)
