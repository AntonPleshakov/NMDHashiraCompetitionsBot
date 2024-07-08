from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup, CallbackQuery

from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    MatchResultTryingToBeChanged,
    MatchResultWasAlreadyRegistered,
    MatchWithPlayersNotFound,
    TechWinCannotBeChanged,
)
from tg.utils import (
    Button,
    empty_filter,
    get_ids,
    report_to_admins,
)
from tournament.tournament_manager import tournament_manager


def apply_result_offer(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Offer to apply result for {cb_query.from_user.username}")
    user_id, chat_id, message_id = get_ids(cb_query)

    for result in tournament_manager.tournament.db.get_results():
        if result.second_id.value == user_id:
            break
        if result.first_id.value == user_id:
            if not result.second:
                nmd_logger.info(f"Offer not shown, user has a technical win")
                bot.answer_callback_query(cb_query.id, text="У вас техническая победа")
                return
            break

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Выиграл", "tournament/won").inline())
    keyboard.add(Button("Проиграл", "tournament/lose").inline())
    bot.send_message(
        chat_id,
        "Сообщите ваш результат\nP.S. неявка, сдача и т.д. оцениваются как поражение",
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
        bot.answer_callback_query(cb_query.id, "Ваш результат зарегистрирован")
    except MatchResultTryingToBeChanged:
        nmd_logger.warning(
            f"MatchResultTryingToBeChanged exception for user {cb_query.from_user.username}"
        )
        bot.answer_callback_query(
            cb_query.id,
            text="Вы пытаетесь зарегистрировать результат, отличный от уже зарегистрированного.\n"
            + "Свяжитесь с одним из администраторов, если вы хотите оспорить зарегистрированный результат.",
            show_alert=True,
        )
        report_to_admins(
            bot,
            f"{cb_query.from_user.username} пытается зарегистрировать результат, отличный от зарегистрированного.\n"
            + f"Data: {cb_query.data}",
        )
    except TechWinCannotBeChanged:
        nmd_logger.info(
            f"TechWinCannotBeChanged exception for user {cb_query.from_user.username}"
        )
        bot.answer_callback_query(cb_query.id, text="У вас техническая победа")
    except MatchResultWasAlreadyRegistered:
        nmd_logger.info(
            f"MatchResultWasAlreadyRegistered exception for user {cb_query.from_user.username}"
        )
        bot.answer_callback_query(cb_query.id, text="Ваш результат уже зарегистрирован")
    except MatchWithPlayersNotFound:
        nmd_logger.warning(f"{cb_query.from_user.username} wasn't found in any match")
        bot.answer_callback_query(
            cb_query.id,
            text="К сожалению мы не смогли найти вас среди участников. Возможна ошибка, свяжитесь с администратором",
            show_alert=True,
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
