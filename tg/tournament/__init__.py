from datetime import timedelta

from telebot import TeleBot
from telebot.types import (
    CallbackQuery,
    InlineKeyboardMarkup,
    Message,
)

from db.admins import admins_db
from db.global_settings import settings_db
from logger.NMDLogger import nmd_logger
from tg.tournament import start_new, update_match_result, new_tour, register
from tg.utils import (
    Button,
    empty_filter,
    get_ids,
    get_like_emoji,
    tournament_timer,
    get_dislike_emoji,
)


def tournament_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Tournament main menu for {cb_query.from_user.username}")
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.delete_state(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Начать турнир", "tournament/start_new").inline())
    keyboard.add(
        Button("Изменить результат матча", "tournament/update_match_result").inline()
    )
    keyboard.add(
        Button("Остановить турнирный таймер", "tournament/stop_timer").inline()
    )
    keyboard.add(Button("Назад в меню", "home").inline())

    text = "Управление турниром"

    remaining = tournament_timer.remaining()
    print(f"Remaining time: {remaining}")
    if remaining > 0:
        text += f"\nТурнирный таймер: {str(timedelta(seconds=remaining))}"
    else:
        text += "\nТурнирный таймер не активен"

    bot.edit_message_text(
        text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def stop_timer(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"{cb_query.from_user.username} stopped the tournament timer")
    tournament_timer.cancel()
    bot.answer_callback_query(cb_query.id, "Таймер остановлен")


def register_chat_id(message: Message, bot: TeleBot):
    user_id, chat_id, message_id = get_ids(message)
    if not admins_db.is_admin(user_id):
        bot.set_message_reaction(chat_id, message_id, get_dislike_emoji())
        bot.send_message(user_id, "Только администратор может менять настройки бота")
        return

    thread_id = message.message_thread_id
    nmd_logger.info(f"Register chat {chat_id}::{thread_id} as tournament")

    settings = settings_db.settings
    settings.chat_id.value = chat_id
    settings.tournament_thread_id.value = thread_id
    settings_db.settings = settings
    bot.set_message_reaction(chat_id, message_id, get_like_emoji())
    bot.send_message(
        user_id, f"Чат {chat_id}::{thread_id} зарегистрирован как турнирный"
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        tournament_main_menu,
        func=empty_filter,
        button="tournament",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        stop_timer,
        func=empty_filter,
        button="tournament/stop_timer",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        register_chat_id,
        commands=["mark_as_tournament_thread"],
        pass_bot=True,
    )

    new_tour.register_handlers(bot)
    register.register_handlers(bot)
    start_new.register_handlers(bot)
    update_match_result.register_handlers(bot)
