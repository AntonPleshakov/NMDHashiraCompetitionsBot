from typing import Union

from telebot import TeleBot
from telebot.types import (
    Message,
    CallbackQuery,
)

from tg import global_settings
from . import admins, dev, ratings, tournament, users
from .utils import empty_filter, home


def home_command(message: Union[Message, CallbackQuery], bot: TeleBot):
    home(message, bot)


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
    global_settings.register_handlers(bot)
    ratings.register_handlers(bot)
    tournament.register_handlers(bot)
    users.register_handlers(bot)
