from typing import Any, Literal, Union
from .utils import JsonObj, ParsedJson


class User(ParsedJson):
    # https://core.telegram.org/bots/api#user
    __id_field__ = "id"
    id: int = 0
    is_bot: bool = False
    first_name: str = ""
    last_name: str = ""
    username: str = ""
    language_code: str = ""


class Chat(ParsedJson):
    # https://core.telegram.org/bots/api#chat
    __id_field__ = "id"
    id: int = 0
    type: Literal["private", "group", "supergroup", "channel"] = ""
    title: str = ""
    is_forum: bool = False


class MessageEntity(JsonObj):
    class _User(JsonObj):
        def __init__(self, id: int):
            self.id = id

    Type = Literal["mention", "hashtag", "cashtag", "bot_command", "url", "email", "phone_number", "bold", "italic", "underline",
                   "strikethrough", "spoiler", "blockquote", "expandable_blockquote", "code", "pre", "text_link", "text_mention", "custom_emoji"]
    # https://core.telegram.org/bots/api#messageentity
    type: Type
    offset: int
    length: int
    url: str = None
    user: _User = None
    language: str = None
    custom_emoji_id: str = None

    def __init__(self, type: Type, offset: int, length: int):
        self.type = type
        self.offset = offset
        self.length = length

    @staticmethod
    def text_mention(offset: int, length: int, user_id: int):
        me = MessageEntity("text_mention", offset, length)
        me.user = MessageEntity._User(user_id)
        return me

    @staticmethod
    def text_link(offset: int, length: int, url: str):
        me = MessageEntity("text_link", offset, length)
        me.url = url
        return me

    @staticmethod
    def blockquote(offset: int, length: int):
        return MessageEntity("blockquote", offset, length)

    @staticmethod
    def spoiler(offset: int, length: int):
        return MessageEntity("spoiler", offset, length)

    @staticmethod
    def bold(offset: int, length: int):
        return MessageEntity("bold", offset, length)

    @staticmethod
    def italic(offset: int, length: int):
        return MessageEntity("italic", offset, length)

    @staticmethod
    def underline(offset: int, length: int):
        return MessageEntity("underline", offset, length)

    @staticmethod
    def len(text: str):
        return len(text.encode("utf-16-le")) // 2

    def copy(self):
        me = MessageEntity(self.type, self.offset, self.length)
        me.url = self.url
        me.user = self.user
        me.language = self.language
        me.custom_emoji_id = self.custom_emoji_id
        return me


class Message(ParsedJson):
    __id_field__ = "message_id"
    # https://core.telegram.org/bots/api#message
    message_id: int = 0
    message_thread_id: int = None
    sender: User = None
    chat: Chat = None
    reply_to_message: "Message" = None
    is_topic_message: bool = False
    text: str = ""
    date: int = 0

    def _parse_field(self, key: str, v: Any, json):
        if key == "from":
            return "sender", User(v)
        if key == "reply_to_message":
            return "reply_to_message", Message(v)


class InlineQuery(ParsedJson):
    # https://core.telegram.org/bots/api#inlinequery
    __id_field__ = "id"
    id: str = ""
    sender: User = None
    query: str = ""
    offset: str = ""
    chat_type: Literal["sender", "private", "group", "supergroup", "channel"] = ""

    def _parse_field(self, key: str, v: Any, json):
        if key == "from":
            return "sender", User(v)


MaybeInaccessibleMessage = Message


class CallbackQuery(ParsedJson):
    # https://core.telegram.org/bots/api#callbackquery
    __id_field__ = "id"
    id: str = ""
    sender: User = None
    message: MaybeInaccessibleMessage = None
    inline_message_id: str = ""
    chat_instance: str = ""
    data: str = ""
    game_short_name: str = ""

    def _parse_field(self, key: str, v: Any, json):
        if key == "from":
            return "sender", User(v)


class ChosenInlineResult(ParsedJson):
    # https://core.telegram.org/bots/api#choseninlineresult
    __id_field__ = "result_id"
    result_id: str = ""
    sender: User = None
    # location: Location
    inline_message_id: str = ""
    query: str = ""

    def _parse_field(self, key: str, v: Any, json):
        if key == "from":
            return "sender", User(v)


class Update(ParsedJson):
    # https://core.telegram.org/bots/api#update
    __id_field__ = "update_id"
    update_id: int = 0
    message: Message = None
    inline_query: InlineQuery = None
    callback_query: CallbackQuery = None
    chosen_inline_result: ChosenInlineResult = None


class InputMessageContent(JsonObj):
    # https://core.telegram.org/bots/api#inputmessagecontent
    pass


class InputTextMessageContent(InputMessageContent):
    # https://core.telegram.org/bots/api#inputtextmessagecontent
    message_text: str
    parse_mode: Literal["MarkdownV2"]
    # entities: list[MessageEntity]
    # link_preview_options: LinkPreviewOptions

    def __init__(self, message_text, use_markdown=False) -> None:
        self.message_text = message_text
        self.parse_mode = "MarkdownV2" if use_markdown else None


class CallbackGame(JsonObj):
    # https://core.telegram.org/bots/api#callbackgame
    pass


class InlineKeyboardButton(JsonObj):
    # https://core.telegram.org/bots/api#inlinekeyboardbutton
    text: str
    url: str = None
    callback_data: str = None
    # web_app: WebAppInfo
    # login_url: LoginUrl
    # switch_inline_query: str
    switch_inline_query_current_chat: str
    # switch_inline_query_chosen_chat: SwitchInlineQueryChosenChat
    # copy_text: CopyTextButton
    callback_game: CallbackGame = None
    # pay: bool

    def __init__(self, text: str) -> None:
        self.text = text

    @staticmethod
    def callback(text: str, callback_data: str):
        b = InlineKeyboardButton(text)
        b.callback_data = callback_data
        return b

    @staticmethod
    def inline_query_current_chat(text: str, query: str):
        b = InlineKeyboardButton(text)
        b.switch_inline_query_current_chat = query
        return b

    @staticmethod
    def run_game(text: str):
        b = InlineKeyboardButton(text)
        b.callback_game = CallbackGame()
        return b

    @staticmethod
    def open_url(text: str, url: str):
        b = InlineKeyboardButton(text)
        b.url = url
        return b


class InlineKeyboardMarkup(JsonObj):
    # https://core.telegram.org/bots/api#inlinekeyboardmarkup
    inline_keyboard: list[list[InlineKeyboardButton]]

    def __init__(self, inline_keyboard: list[list[InlineKeyboardButton]]) -> None:
        self.inline_keyboard = inline_keyboard


class InlineQueryResult(JsonObj):
    # https://core.telegram.org/bots/api#inlinequeryresult
    pass


class InlineQueryResultArticle(InlineQueryResult):
    # https://core.telegram.org/bots/api#inlinequeryresultarticle
    type = "article"
    id: str
    title: str
    input_message_content: InputMessageContent
    # reply_markup: InlineKeyboardMarkup
    url: str = None
    hide_url: bool = None
    description: str = None
    thumbnail_url: str = None
    thumbnail_width: int = None
    thumbnail_height: int = None

    def __init__(self, id: str, title: str, input_message_content: InputMessageContent) -> None:
        self.id = id
        self.title = title
        self.input_message_content = input_message_content


class InlineQueryResultGame(InlineQueryResult):
    # https://core.telegram.org/bots/api#inlinequeryresultgame
    type = "game"
    id: str
    game_short_name: str
    reply_markup: InlineKeyboardMarkup = None

    def __init__(self, id: str, game_short_name: str, reply_markup: InlineKeyboardMarkup = None) -> None:
        self.id = id
        self.game_short_name = game_short_name
        self.reply_markup = reply_markup


class BotCommand(JsonObj):
    # https://core.telegram.org/bots/api#botcommand
    command: str  # 1-32 characters. Can contain only lowercase English letters, digits and underscores.
    description: str  # 1-256 characters.

    def __init__(self, command: str, description: str):
        self.command = command
        self.description = description


class ChatMember(ParsedJson):
    # https://core.telegram.org/bots/api#chatmember
    status: Literal["creator", "administrator", "member", "restricted", "left", "kicked"] = ""
    user: User = None


BotCommandScopeType = Literal["default", "all_private_chats", "all_group_chats",
                              "all_chat_administrators", "chat", "chat_administrators", "chat_member"]


class BotCommandScope(JsonObj):
    # https://core.telegram.org/bots/api#botcommandscope
    type: BotCommandScopeType = "default"
    chat_id: Union[str, int]
    user_id: int

    def __init__(self, type: BotCommandScopeType):
        self.type = type

    @staticmethod
    def default():
        return BotCommandScope("default")

    @staticmethod
    def all_private_chats():
        return BotCommandScope("all_private_chats")

    @staticmethod
    def all_group_chats():
        return BotCommandScope("all_group_chats")

    @staticmethod
    def all_chat_administrators():
        return BotCommandScope("all_chat_administrators")

    @staticmethod
    def chat(chat_id: Union[str, int]):
        scope = BotCommandScope("chat")
        scope.chat_id = chat_id
        return scope

    @staticmethod
    def chat_administrators(chat_id: Union[str, int]):
        scope = BotCommandScope("chat_administrators")
        scope.chat_id = chat_id
        return scope

    @staticmethod
    def chat_member(chat_id: Union[str, int], user_id: int):
        scope = BotCommandScope("chat_member")
        scope.chat_id = chat_id
        scope.user_id = user_id
        return scope


class ReplyParameters(JsonObj):
    # https://core.telegram.org/bots/api#replyparameters
    message_id: int

    def __init__(self, message_id: int):
        self.message_id = message_id


class LinkPreviewOptions(JsonObj):
    # https://core.telegram.org/bots/api#linkpreviewoptions
    is_disabled: bool
    url: str
    prefer_small_media: bool
    prefer_large_media: bool
    show_above_text: bool

    @staticmethod
    def disable():
        lpo = LinkPreviewOptions()
        lpo.is_disabled = True
        return lpo


class InputMedia(JsonObj):
    # https://core.telegram.org/bots/api#inputmedia
    type: Literal["photo", "video", "animation", "audio", "document"]
    media: str
    caption: str = None
    parse_mode: Union[Literal["MarkdownV2"], None] = None
    caption_entities: list[MessageEntity] = []
    show_caption_above_media: bool = False
    has_spoiler: bool = False

    def __init__(self, media: str):
        self.media = media

    def set_caption(self, caption: str = None, parse_mode: Union[Literal["MarkdownV2"], None] = None,
                    caption_entities: list[MessageEntity] = [], show_caption_above_media: bool = False, has_spoiler: bool = False):
        self.caption = caption
        self.parse_mode = parse_mode
        self.caption_entities = caption_entities
        self.show_caption_above_media = show_caption_above_media
        self.has_spoiler = has_spoiler
        return self


class InputMediaPhoto(InputMedia):
    # https://core.telegram.org/bots/api#inputmediaphoto
    type = "photo"


class InputMediaVideo(InputMedia):
    # https://core.telegram.org/bots/api#inputmediavideo
    type = "video"
    thumbnail: str
    cover: str
    start_timestamp: int
    width: int
    height: int
    duration: int
    supports_streaming: bool


class InputMediaAnimation(InputMedia):
    # https://core.telegram.org/bots/api#inputmediaanimation
    type = "animation"
    thumbnail: str
    width: int
    height: int
    duration: int


class InputMediaAudio(InputMedia):
    # https://core.telegram.org/bots/api#inputmediaaudio
    type = "audio"
    thumbnail: str
    duration: int
    performer: str
    title: str


class InputMediaDocument(InputMedia):
    # https://core.telegram.org/bots/api#inputmediadocument
    type = "document"
    thumbnail: str
    disable_content_type_detection: bool
