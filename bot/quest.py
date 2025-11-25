import bafser_tgapi as tgapi
from bafser import Undefined

from bot.bot import Bot
from bot.utils import silent_mode
from data.quest import Quest


@Bot.add_command()
@Bot.cmd_for_quest
def set_reward(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.chat or not bot.message:
        return
    q = Quest.get_by_topic(bot.chat.id, Undefined.default(bot.message.message_thread_id, 0))
    if not q:
        return "Quest not found."
    if len(args) != 1:
        return "Usage: /set_reward <reward>"
    old_reward = q.reward
    q.set_reward(int(args[0]))
    return f"Quest reward changed: {old_reward} -> {q.reward}"


@Bot.add_command()
def get_chat_id(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    if not bot.chat:
        return "Chat ID is not available."
    return str(bot.chat.id)


@Bot.on_forum_topic_created
def on_forum_topic_created(bot: Bot):
    if not bot.chat or str(bot.chat.id) != bot._quest_room_id or not bot.message:
        return
    if not Undefined.defined(bot.message.forum_topic_created):
        return
    q = Quest.new(bot.message.forum_topic_created.name, bot.chat.id, Undefined.default(bot.message.message_thread_id, 0))
    bot.sendMessage(f"Quest {bot.message.forum_topic_created.name} created!", reply_markup=tgapi.reply_markup([
        tgapi.InlineKeyboardButton.open_url("Open Scanner", tgapi.utils.url + f"scanner?uid={bot.user.id_big}&id={q.id}"),

    ]))


@Bot.on_forum_topic_edited
def on_forum_topic_edited(bot: Bot):
    if not bot.chat or str(bot.chat.id) != bot._quest_room_id or not bot.message:
        return
    if not Undefined.defined(bot.message.forum_topic_edited):
        return
    q = Quest.get_by_topic(bot.chat.id, Undefined.default(bot.message.message_thread_id, 0))
    if not q:
        q = Quest.new(bot.message.forum_topic_edited.name, bot.chat.id, Undefined.default(bot.message.message_thread_id, 0))
        bot.sendMessage(f"Quest {bot.message.forum_topic_edited.name} created!", reply_markup=tgapi.reply_markup([
            tgapi.InlineKeyboardButton.open_url("Open Scanner", tgapi.utils.url + f"scanner?uid={bot.user.id_big}&id={q.id}"),
        ]))
    else:
        old_name = q.name
        q.update_name(bot.message.forum_topic_edited.name)
        bot.sendMessage(f"Quest name changed: {old_name} -> {q.name}", reply_markup=tgapi.reply_markup([
            tgapi.InlineKeyboardButton.open_url("Open Scanner", tgapi.utils.url + f"scanner?uid={bot.user.id_big}&id={q.id}"),
        ]))
