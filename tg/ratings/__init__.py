from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from tg.ratings import update_rating, delete_rating
from tg.utils import Button, empty_filter, get_ids


def ratings_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.delete_state(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Изменить рейтинг", "ratings/update_rating").inline())
    keyboard.add(Button("Удалить рейтинг", "ratings/delete_rating").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление списком рейтингов",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        ratings_main_menu,
        func=empty_filter,
        button="ratings",
        is_private=True,
        pass_bot=True,
    )

    delete_rating.register_handlers(bot)
    update_rating.register_handlers(bot)
