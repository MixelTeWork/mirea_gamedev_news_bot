import bafser_tgapi as tgapi
from bafser import Undefined

from bot.bot import Bot
from bot.utils import silent_mode
from data.quest import Quest
from data.user_quest import UserQuest


@Bot.add_command()
def start(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    txt = "Добро пожаловать в мир МИРЭА Геймдева! 🎮\n\n" \
        "Чтобы быть в курсе всех новостей, подпишитесь на нашу рассылку!\n\n" \
        "✨ Начните своё приключение и посетите все контрольные точки!"
    bot.sendMessage(txt, reply_markup=tgapi.reply_markup(
        [("📨 Подписаться", "subscribe")],
        [("🎮 Начать приключение!", "start_quest")]
    ))


@Bot.add_command()
def start_quest(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    txt = "Приключение начинается! 🔥\n\n" \
        "Чтобы засчитать ваш прогресс и завершить квест, покажите свой QR-Код квестовику!"

    bot.sendMessage(txt, reply_markup=tgapi.reply_markup(
        [("Мой прогресс ✨", "quest_points")],
    ))
    bot.sendPhoto(tgapi.utils.url + f"qr?data={bot.user.id_big}")


@Bot.add_command()
def quest_points(bot: Bot, args: tgapi.BotCmdArgs, **_: str):
    quests = UserQuest.get_completed_quests(bot.user)
    xp = 0
    for q in quests:
        xp += q.reward
    # xp = UserQuest.get_user_points(bot.user)
    txt = f"✨ Ваш текущий XP: {xp}"
    if len(quests) > 0:
        txt += "\nЗавершенные квесты:\n" + "\n".join(f"• {q.name} ({q.reward} xp)" for q in quests)
    bot.sendMessage(txt, reply_markup=tgapi.reply_markup(
        [("Обновить ✨", "quest_points")],
    ))


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
    return f"Награда за квест успешно изменена: {old_reward} -> {q.reward}"


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
    txt = f"Квест {q.name} создан!\n\n" + \
        f"Награда: {q.reward} xp\nИзменить награду: /set_reward <целое число>"
    bot.sendMessage(txt, reply_markup=tgapi.reply_markup(
        [tgapi.InlineKeyboardButton.open_url("Открыть сканер", tgapi.utils.url + f"scanner?uid={bot.user.id_big}&id={q.id}")],
    ))


@Bot.on_forum_topic_edited
def on_forum_topic_edited(bot: Bot):
    if not bot.chat or str(bot.chat.id) != bot._quest_room_id or not bot.message:
        return
    if not Undefined.defined(bot.message.forum_topic_edited):
        return
    q = Quest.get_by_topic(bot.chat.id, Undefined.default(bot.message.message_thread_id, 0))
    if not q:
        q = Quest.new(bot.message.forum_topic_edited.name, bot.chat.id, Undefined.default(bot.message.message_thread_id, 0))
        txt = f"Квест {q.name} создан!\n\n" + \
            f"Награда: {q.reward} xp\nИзменить награду: /set_reward <целое число>"
        bot.sendMessage(txt, reply_markup=tgapi.reply_markup(
            [tgapi.InlineKeyboardButton.open_url("Открыть сканер", tgapi.utils.url + f"scanner?uid={bot.user.id_big}&id={q.id}")],
        ))
    else:
        old_name = q.name
        q.update_name(bot.message.forum_topic_edited.name)
        bot.sendMessage(f"Название квеста изменено: {old_name} -> {q.name}", reply_markup=tgapi.reply_markup([
            tgapi.InlineKeyboardButton.open_url("Открыть сканер", tgapi.utils.url + f"scanner?uid={bot.user.id_big}&id={q.id}"),
        ]))
