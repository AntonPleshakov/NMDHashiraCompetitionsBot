from typing import Union

from telebot import TeleBot
from telebot.handler_backends import BaseMiddleware
from telebot.types import CallbackQuery, Message

import tg.manager
from config.config import getconf
from logger.NMDLogger import nmd_logger
from tg.filters import add_custom_filters
from tg.utils import (
    empty_filter,
    get_permissions_denied_message,
    get_ids,
    get_user_view,
)

bot = TeleBot(getconf("TOKEN"), parse_mode="HTML", use_class_middlewares=True)


class AlwaysAnswerCallbackQueryMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()
        self.update_types = ["callback_query"]
        self._ignore_data = {"tournament/register", "tournament/(won|lose)"}

    def pre_process(self, message: CallbackQuery, data: dict):
        if message.data not in self._ignore_data:
            bot.answer_callback_query(message.id)

    def post_process(
        self, message: CallbackQuery, data: dict, exception: BaseException
    ):
        pass


def permission_denied_message(message: Union[Message, CallbackQuery]):
    nmd_logger.info(f"Permission denied for user '{get_user_view(message)}'")
    user_id, chat_id, _ = get_ids(message)
    denied_text = get_permissions_denied_message(user_id)
    if isinstance(message, Message):
        bot.reply_to(message=message, text=denied_text)
    else:
        bot.send_message(chat_id=chat_id, text=denied_text)


if __name__ == "__main__":
    nmd_logger.info("Bot started")
    add_custom_filters(bot)
    tg.manager.register_handlers(bot)
    bot.register_message_handler(
        permission_denied_message,
        chat_types=["private"],
        is_admin=False,
    )
    bot.register_callback_query_handler(
        permission_denied_message,
        func=empty_filter,
        is_private=True,
        is_admin=False,
    )
    bot.setup_middleware(AlwaysAnswerCallbackQueryMiddleware())
    bot.infinity_polling()
