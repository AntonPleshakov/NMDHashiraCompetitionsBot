import logging

import telebot

from config.config import getconf
from db.admins_db import admins_db
from tg.tg_manager import process_command, get_permissions_denied_message
from tg.tg_utils import BTN_TEXT

bot = telebot.TeleBot(getconf("TOKEN"), parse_mode="MarkdownV2")
telebot.logger.setLevel(logging.INFO)


@bot.message_handler(chat_types=["private"], content_types=["text"])
def start_mes(message: telebot.types.Message):
    if not admins_db.is_admin(message.from_user.id):
        bot.reply_to(message, text=get_permissions_denied_message())
        return
    keyboard = process_command()
    bot.send_message(
        chat_id=message.chat.id,
        text="Выберите раздел управления",
        reply_markup=keyboard,
    )


@bot.message_handler(chat_types=["private"], content_types=["user_shared"])
def add_admin(message: telebot.types.Message):
    pass


@bot.callback_query_handler(func=lambda callback_query: True)
def echo_message(callback_query: telebot.types.CallbackQuery):
    keyboard = process_command(callback_query.data)
    btn_data = callback_query.data.split("/")[-1]
    if btn_data == "home_button":
        btn_data = "root"
    bot.edit_message_text(
        text=BTN_TEXT[btn_data],
        chat_id=callback_query.message.chat.id,
        message_id=callback_query.message.id,
        reply_markup=keyboard,
    )


if __name__ == "__main__":
    bot.infinity_polling()
