from typing import Union

from telebot import TeleBot
from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from . import admins, dev, ratings, tournament
from .utils import empty_filter, Button


def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Администраторы", "admins").inline())
    keyboard.add(Button("Рейтинги", "ratings").inline())
    keyboard.add(Button("Турнир", "tournament").inline())
    keyboard.add(Button("Служебные", "dev").inline())
    return keyboard


def home_command(message: Union[Message, CallbackQuery], bot: TeleBot):
    keyboard = main_menu_keyboard()
    text = "Выберите раздел управления"
    if isinstance(message, CallbackQuery):
        chat_id = message.message.chat.id
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message.message.id,
            reply_markup=keyboard,
        )
    else:
        chat_id = message.chat.id
        bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
        )
    user_id = message.from_user.id
    bot.reset_data(user_id, chat_id)


def register_handlers(bot: TeleBot):
    bot.register_message_handler(
        home_command, commands=["start"], chat_types=["private"], pass_bot=True
    )
    bot.register_callback_query_handler(
        home_command, func=empty_filter, button="home", is_private=True, pass_bot=True
    )

    admins.register_handlers(bot)
    dev.register_handlers(bot)
    ratings.register_handlers(bot)
    tournament.register_handlers(bot)
