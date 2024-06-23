from typing import List

from telebot.types import InlineKeyboardMarkup, CallbackQuery

from config.config import getconf
from db.admins import admins_db
from db.tournament_structures import Match
from main import bot
from nmd_exceptions import MatchResultTryingToBeChanged
from tg.utils import Button, empty_filter, get_ids, get_next_tour_message
from tournament.tournament_manager import tournament_manager


def announce_new_tour(pairs: List[Match]):
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


def apply_result_offer(cb_query: CallbackQuery):
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


def apply_result(cb_query: CallbackQuery):
    user_id, chat_id, message_id = get_ids(cb_query)
    try:
        tournament_manager.tournament.add_result(
            user_id, "tournament/won" == cb_query.data
        )
    except MatchResultTryingToBeChanged:
        admins_list = [
            f"[{admin.username}](tg://user?id={admin.user_id})"
            for admin in admins_db.get_admins()
        ]
        bot.send_message(
            chat_id=user_id,
            text="Вы пытаетесь зарегистрировать результат\, отличный от уже зарегистрированного\.\n"
            + "Свяжитесь с одним из администраторов\, если вы хотите оспорить зарегистрированный результат\.\n"
            + "Список администраторов\: "
            + "\, ".join(admins_list),
        )
    bot.delete_message(chat_id, message_id)


def register_handlers():
    bot.register_callback_query_handler(
        apply_result_offer,
        func=empty_filter,
        button="tournament/apply_result",
        is_private=False,
    )
    bot.register_callback_query_handler(
        apply_result,
        func=empty_filter,
        button="tournament/(won|lose)",
        is_private=False,
    )
