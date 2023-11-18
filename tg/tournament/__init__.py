from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from tg.tournament import start_new, update_match_result
from tg.utils import Button, empty_filter, get_ids


def tournament_main_menu(cb_query: CallbackQuery, bot: TeleBot):
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


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        tournament_main_menu,
        func=empty_filter,
        button="tournament",
        is_private=True,
        pass_bot=True,
    )

    start_new.register_handlers(bot)
    update_match_result.register_handlers(bot)
