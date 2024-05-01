import logging

from telebot import TeleBot, logger
from telebot.handler_backends import BaseMiddleware
from telebot.types import Message, CallbackQuery

import tg.manager
from config.config import getconf
from tg.filters import add_custom_filters
from tg.utils import (
    get_permissions_denied_message,
)

bot = TeleBot(getconf("TOKEN"), parse_mode="MarkdownV2", use_class_middlewares=True)
logger.setLevel(logging.INFO)


class AlwaysAnswerCallbackQueryMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ["callback_query"]
        self._ignore_data = {"tournament/register"}

    def pre_process(self, message: CallbackQuery, data: dict):
        if message.data not in self._ignore_data:
            bot.answer_callback_query(message.id)

    def post_process(
        self, message: CallbackQuery, data: dict, exception: BaseException
    ):
        pass


@bot.message_handler(chat_types=["private"], is_admin=False)
def permission_denied_message(message: Message):
    bot.reply_to(message, text=get_permissions_denied_message(message.from_user.id))


@bot.callback_query_handler(func=None, is_private=True, is_admin=False)
def permission_denied_callback(callback_query: CallbackQuery):
    bot.send_message(
        callback_query.message.chat.id,
        text=get_permissions_denied_message(callback_query.from_user.id),
    )
    bot.answer_callback_query(callback_query.id)


if __name__ == "__main__":
    add_custom_filters(bot)
    tg.manager.register_handlers(bot)
    bot.setup_middleware(AlwaysAnswerCallbackQueryMiddleware())
    bot.infinity_polling()
