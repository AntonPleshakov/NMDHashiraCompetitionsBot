from typing import Union

from telebot import TeleBot
from telebot.types import (
    Message,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from tg import tg_admins
from tg.tg_utils import empty_filter, Button


def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Администраторы", "admins").inline())
    keyboard.add(Button("Рейтинги", "ratings").inline())
    keyboard.add(Button("Турнир", "tournament").inline())
    keyboard.add(Button("Служебное", "dev").inline())
    return keyboard


def home_command(message: Union[Message, CallbackQuery], bot: TeleBot):
    keyboard = main_menu_keyboard()
    text = "Выберите раздел управления"
    if isinstance(message, CallbackQuery):
        bot.edit_message_text(
            text=text,
            chat_id=message.message.chat.id,
            message_id=message.message.id,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard,
        )
    return True


def register_handlers(bot: TeleBot):
    bot.register_message_handler(
        home_command, commands=["start"], chat_types=["private"], pass_bot=True
    )
    bot.register_callback_query_handler(
        home_command, func=empty_filter, button="home", is_private=True, pass_bot=True
    )

    tg_admins.register_handlers(bot)
