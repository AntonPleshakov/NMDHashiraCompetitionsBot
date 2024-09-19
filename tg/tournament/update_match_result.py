from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from db.tournament_structures import Match
from logger.NMDLogger import nmd_logger
from nmd_exceptions import TournamentNotStartedError
from tg.tournament.announcements import update_tour_message
from tg.utils import Button, empty_filter, get_ids, home, get_username
from tournament.tournament_manager import tournament_manager


class UpdateMatchStates(StatesGroup):
    tour_to_update = State()
    match_to_update = State()
    new_result = State()


def chose_match_to_update(cb_query: CallbackQuery, bot: TeleBot):
    username = get_username(cb_query)
    nmd_logger.info(f"Chose match to update for {username}")
    try:
        matches = tournament_manager.tournament.db.get_results()
        keyboard = InlineKeyboardMarkup(row_width=1)
        for i, match in enumerate(matches):
            text = match.to_string()
            keyboard.add(Button(text, f"{i}").inline())
        keyboard.add(Button("Назад в Турнир", "tournament").inline())

        user_id, chat_id, message_id = get_ids(cb_query)
        bot.edit_message_text(
            text="Выберите матч для редактирования результата",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
        )
        bot.set_state(user_id, UpdateMatchStates.match_to_update)
    except TournamentNotStartedError:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(Button("Назад в Турнир", "tournament").inline())

        _, chat_id, message_id = get_ids(cb_query)
        bot.edit_message_text(
            text="Турнир еще не начался",
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
        )


def chose_result_to_update_match(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(
        f"Match to update was chosen: {tournament_manager.tournament.db.get_results()[int(cb_query.data)].to_string()}"
    )
    match_index = int(cb_query.data)
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.add_data(user_id, match_index=match_index)

    match = tournament_manager.tournament.db.get_results()[match_index]
    keyboard = InlineKeyboardMarkup(row_width=1)
    for res in Match.MatchResult:
        new_result = Match.MATCH_RESULT_TO_STR[res]
        if new_result == match.result.value:
            continue
        text = f"{match.first.value} {new_result} {match.second.value}"
        keyboard.add(Button(text, f"{new_result}").inline())
    keyboard.add(Button("Назад в Турнир", "tournament").inline())
    bot.edit_message_text(
        text="Выберите новый результат",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )
    bot.set_state(user_id, UpdateMatchStates.new_result)


def update_result(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"New result: {cb_query.data}")
    user_id, chat_id, _ = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        match_index = data["match_index"]
    if cb_query.data not in Match.STR_TO_MATCH_RESULT:
        nmd_logger.error(f"Error: new result is unsupported: {cb_query.data}")
    new_result = Match.STR_TO_MATCH_RESULT[cb_query.data]

    tournament = tournament_manager.tournament
    match = tournament.db.get_results()[match_index]

    tournament.add_result(
        match.first_id.value, new_result == Match.MatchResult.FirstWon, True
    )
    update_tour_message(tournament.db, bot)
    bot.answer_callback_query(cb_query.id, text="Результат успешно изменен")
    bot.delete_state(user_id)
    home(cb_query, bot)


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        chose_match_to_update,
        func=empty_filter,
        button="tournament/update_match_result",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        chose_result_to_update_match,
        func=empty_filter,
        state=UpdateMatchStates.match_to_update,
        button=r"\d+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_result,
        func=empty_filter,
        state=UpdateMatchStates.new_result,
        button=r"(1|0):(0|1)",
        is_private=True,
        pass_bot=True,
    )
