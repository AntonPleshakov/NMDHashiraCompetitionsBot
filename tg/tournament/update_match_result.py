from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from tg.utils import Button, empty_filter
from tournament.match import Match, MatchResult, MATCH_RESULT_TO_STR
from tournament.tournament_manager import tournament_manager


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
    matches = tournament_manager.tournament.db.get_results()
    keyboard = InlineKeyboardMarkup(row_width=1)
    for i, match in enumerate(matches):
        text = match_to_string(match)
        keyboard.add(Button(text, f"tournament/update_match_result/{i}").inline())
    keyboard.add(Button("Назад в Турнир", "tournament").inline())
    bot.edit_message_text(
        text="Выберите матч для редактирования результата",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def chose_result_to_update_match(cb_query: CallbackQuery, bot: TeleBot):
    match_index = int(cb_query.data.split("/")[-1])
    match = tournament_manager.tournament.db.get_results()[match_index]
    current_result = match.result
    keyboard = InlineKeyboardMarkup(row_width=1)
    for res in MatchResult:
        if res == current_result:
            continue
        text = match_to_string(match)
        keyboard.add(Button(text, cb_query.data + "/" + res.name).inline())
    keyboard.add(Button("Назад в Турнир", "tournament").inline())
    bot.edit_message_text(
        text="Выберите новый результат",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def update_result(cb_query: CallbackQuery, bot: TeleBot):
    match_index = int(cb_query.data.split("/")[-2])
    new_result = MatchResult[cb_query.data.split("/")[-1]]
    tournament_manager.tournament.db.register_result(match_index, new_result)
    bot.send_message(chat_id=cb_query.message.chat.id, text="Результат успешно изменен")


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
