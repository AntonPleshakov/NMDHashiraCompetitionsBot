from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from nmd_exceptions import TournamentNotStartedError
from tg.utils import Button, empty_filter, get_ids
from tournament.match import Match, MatchResult, MATCH_RESULT_TO_STR
from tournament.tournament_manager import tournament_manager


class UpdateMatchStates(StatesGroup):
    match_to_update = State()
    new_result = State()


def match_to_string(match: Match):
    text = f"{match.first_player}"
    if match.result == MatchResult.Tie:
        text += f" ({MATCH_RESULT_TO_STR[match.result]}) "
    elif match.result != MatchResult.NotPlayed:
        text += f" {MATCH_RESULT_TO_STR[match.result]} "
    else:
        text += " : "
    text += f"{match.second_player}"
    return text


def chose_match_to_update(cb_query: CallbackQuery, bot: TeleBot):
    try:
        matches = tournament_manager.tournament.db.get_results()
        keyboard = InlineKeyboardMarkup(row_width=1)
        for i, match in enumerate(matches):
            text = match_to_string(match)
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
    match_index = int(cb_query.data)
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.add_data(user_id, match_index=match_index)

    match = tournament_manager.tournament.db.get_results()[match_index]
    current_result = match.result
    keyboard = InlineKeyboardMarkup(row_width=1)
    for res in MatchResult:
        if res == current_result:
            continue
        text = match_to_string(match)
        keyboard.add(Button(text, res.name).inline())
    keyboard.add(Button("Назад в Турнир", "tournament").inline())
    bot.edit_message_text(
        text="Выберите новый результат",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )
    bot.set_state(user_id, UpdateMatchStates.new_result)


def update_result(cb_query: CallbackQuery, bot: TeleBot):
    user_id, chat_id, _ = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        match_index = data["match_index"]
    new_result = MatchResult[cb_query.data]
    tournament_manager.tournament.db.register_result(match_index, new_result)
    bot.send_message(chat_id=chat_id, text="Результат успешно изменен")
    bot.delete_state(user_id)


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
        button="tournament/update_match_result/\d+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_result,
        func=empty_filter,
        button="tournament/update_match_result/\d+/\w+",
        is_private=True,
        pass_bot=True,
    )
