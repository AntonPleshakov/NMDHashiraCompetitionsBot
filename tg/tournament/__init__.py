from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Message

from db.global_settings import settings_db
from logger.NMDLogger import nmd_logger
from tg.tournament import start_new, update_match_result, new_tour, register
from tg.utils import Button, empty_filter, get_ids


def tournament_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Tournament main menu for {cb_query.from_user.username}")
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.delete_state(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Начать турнир", "tournament/start_new").inline())
    keyboard.add(
        Button("Изменить результат матча", "tournament/update_match_result").inline()
    )
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление администраторами",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def register_chat_id(message: Message, bot: TeleBot):
    _, chat_id, message_id = get_ids(message)
    thread_id = message.message_thread_id
    nmd_logger.info(
        f"Register chat_id {chat_id} and thread_id {thread_id} as tournament"
    )
    with settings_db.settings as settings:
        settings.chat_id.value = chat_id
        settings.tournament_thread_id.value = thread_id
    bot.delete_message(chat_id=chat_id, message_id=message_id)


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        tournament_main_menu,
        func=empty_filter,
        button="tournament",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        register_chat_id,
        commands=["mark_as_tournament_thread"],
        is_admin=True,
        pass_bot=True,
    )

    new_tour.register_handlers(bot)
    register.register_handlers(bot)
    start_new.register_handlers(bot)
    update_match_result.register_handlers(bot)
