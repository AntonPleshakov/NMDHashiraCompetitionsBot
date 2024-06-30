from typing import List

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, CallbackQuery

from config.config import getconf
from db.admins import admins_db
from db.tournament_structures import Match
from logger.NMDLogger import nmd_logger
from nmd_exceptions import MatchResultTryingToBeChanged
from tg.utils import (
    Button,
    empty_filter,
    get_ids,
    get_next_tour_message,
    report_to_admins,
)
from tournament.tournament_manager import tournament_manager


def announce_new_tour(bot: TeleBot, pairs: List[Match]):
    nmd_logger.info("New tour announcement")
    chat_id = int(getconf("CHAT_ID"))
    message_thread_id = int(getconf("TOURNAMENT_THREAD_ID"))
    db = tournament_manager.tournament.db
    tours_number = db.get_tours_number()
    settings = tournament_manager.tournament.db.settings
    tournament_url = tournament_manager.tournament.db.get_url()
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Объявить результат", "tournament/apply_result").inline())
    message = bot.send_message(
        chat_id,
        get_next_tour_message(settings, pairs, tours_number, tournament_url),
        reply_markup=keyboard,
        message_thread_id=message_thread_id,
    )
    bot.pin_chat_message(chat_id, message.id)


def apply_result_offer(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Offer to apply result for {cb_query.from_user.username}")
    user_id, chat_id, message_id = get_ids(cb_query)
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Выиграл", "tournament/won").inline())
    keyboard.add(Button("Проиграл", "tournament/lose").inline())
    bot.send_message(
        chat_id,
        "Сообщите ваш результат\nP\.S\. неявка\, сдача и т\.д\. оцениваются как поражение",
        reply_markup=keyboard,
        message_thread_id=cb_query.message.message_thread_id,
    )


def apply_result(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(
        f"User {cb_query.from_user.username} applied result: {cb_query.data}"
    )
    user_id, chat_id, message_id = get_ids(cb_query)
    try:
        tournament_manager.tournament.add_result(
            user_id, "tournament/won" == cb_query.data
        )
        bot.answer_callback_query(message_id)
    except MatchResultTryingToBeChanged:
        nmd_logger.warning(
            f"MatchResultTryingToBeChanged exception for user {cb_query.from_user.username}"
        )
        admins_list = [
            f"[{admin.username}](tg://user?id={admin.user_id})"
            for admin in admins_db.get_admins()
        ]
        bot.answer_callback_query(
            message_id,
            text="Вы пытаетесь зарегистрировать результат\, отличный от уже зарегистрированного\.\n"
            + "Свяжитесь с одним из администраторов\, если вы хотите оспорить зарегистрированный результат\.\n"
            + "Список администраторов\: "
            + "\, ".join(admins_list),
            show_alert=True,
        )
        report_to_admins(
            bot,
            f"{cb_query.from_user.username} пытается зарегистрировать результат\, отличный от зарегистрированного\.\n"
            + f"Data: {cb_query.data}",
        )
    bot.delete_message(chat_id, message_id)


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        apply_result_offer,
        func=empty_filter,
        button="tournament/apply_result",
        is_private=False,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        apply_result,
        func=empty_filter,
        button="tournament/(won|lose)",
        is_private=False,
        pass_bot=True,
    )
