import logging

import telebot

from config.config import getconf
from db.admins_db import admins_db
from tg.tg_manager import (
    process_command,
    get_permissions_denied_message,
    home_command,
)

bot = telebot.TeleBot(getconf("TOKEN"), parse_mode="MarkdownV2")
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(chat_types=["private"], content_types=["text"])
def start_mes(message: telebot.types.Message):
    if not admins_db.is_admin(message.from_user.id):
        bot.reply_to(message, text=get_permissions_denied_message())
        return
    home_command(bot, message)


@bot.message_handler(chat_types=["private"], content_types=["user_shared"])
def add_admin(message: telebot.types.Message):
    pass


@bot.callback_query_handler(func=lambda callback_query: True)
def process_menu_buttons(callback_query: telebot.types.CallbackQuery):
    process_command(bot, callback_query)


if __name__ == "__main__":
    bot.infinity_polling()
