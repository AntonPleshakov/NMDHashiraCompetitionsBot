from typing import Union

from telebot import TeleBot
from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from . import admins, dev, ratings, tournament, users
from .utils import empty_filter, Button, get_ids


def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Администраторы", "admins").inline())
    keyboard.add(Button("Рейтинги", "ratings").inline())
    keyboard.add(Button("Турнир", "tournament").inline())
    keyboard.add(Button("Служебные", "dev").inline())
    keyboard.add(Button("Пользовательские", "users").inline())
    return keyboard


def home_command(message: Union[Message, CallbackQuery], bot: TeleBot):
    keyboard = main_menu_keyboard()
    text = "Выберите раздел управления"
    user_id, chat_id, message_id = get_ids(message)
    if isinstance(message, CallbackQuery):
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
        )
    bot.delete_state(user_id)


def register_handlers(bot: TeleBot):
    bot.register_message_handler(
        home_command,
        commands=["start"],
        chat_types=["private"],
        pass_bot=True,
        is_admin=True,
    )
    bot.register_callback_query_handler(
        home_command, func=empty_filter, button="home", is_private=True, pass_bot=True
    )

    admins.register_handlers(bot)
    dev.register_handlers(bot)
    ratings.register_handlers(bot)
    tournament.register_handlers(bot)
    users.register_handlers(bot)
