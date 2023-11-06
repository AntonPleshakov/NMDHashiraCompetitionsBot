from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from tg.tg_utils import Button, empty_filter


def tournament_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Начать турнир", "tournament/start_new").inline())
    keyboard.add(
        Button("Изменить результат матча", "tournament/update_match_result").inline()
    )
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление администраторами",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    pass


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        tournament_main_menu,
        func=empty_filter,
        button="tournament",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        start_new_tournament,
        func=empty_filter,
        button="tournament/start_new",
        is_private=True,
        pass_bot=True,
    )
