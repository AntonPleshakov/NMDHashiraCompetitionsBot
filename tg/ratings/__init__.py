from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from tg.ratings import update_rating, delete_rating
from tg.utils import Button, empty_filter


def ratings_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    bot.delete_state(cb_query.from_user.id, cb_query.message.chat.id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Изменить рейтинг", "ratings/update_rating").inline())
    keyboard.add(Button("Удалить рейтинг", "ratings/delete_rating").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление списком рейтингов",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
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
