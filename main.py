import logging

from telebot import TeleBot, logger
from telebot.types import Message, CallbackQuery

from config.config import getconf
from tg import tg_manager
from tg.tg_filters import add_custom_filters
from tg.tg_utils import (
    get_permissions_denied_message,
)

bot = TeleBot(getconf("TOKEN"), parse_mode="MarkdownV2")
logger.setLevel(logging.INFO)


@bot.message_handler(chat_types=["private"], is_admin=False)
def permission_denied_message(message: Message):
    bot.reply_to(message, text=get_permissions_denied_message())


@bot.callback_query_handler(func=None, is_private=True, is_admin=False)
def permission_denied_callback(callback_query: CallbackQuery):
    bot.send_message(
        callback_query.message.chat.id, text=get_permissions_denied_message()
    )
    bot.answer_callback_query(callback_query.id)


if __name__ == "__main__":
    add_custom_filters(bot)
    tg_manager.register_handlers(bot)
    bot.infinity_polling()
