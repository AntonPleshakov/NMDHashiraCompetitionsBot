from textwrap import dedent

from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Message

from config.config import getconf
from tournament.match import MATCH_RESULT_TO_STR, MatchResult, Match
from tournament.tournament_manager import tournament_manager
from tournament.tournament_settings import TournamentSettings
from .utils import Button, empty_filter


def tournament_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Начать турнир", "tournament/start_new").inline())
    keyboard.add(
        Button("Изменить результат матча", "tournament/update_match_result").inline()
    )
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление администраторами",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def tournament_start_keyboard(settings: TournamentSettings) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        Button(
            "Запустить с выбранными настройками", "tournament/start_new/confirmed"
        ).inline()
    )
    keyboard.add(
        Button(
            "Изменить количество раундов",
            f"tournament/start_new/edit_rounds_number/{settings.to_data()}",
        ).inline()
    )
    keyboard.add(
        Button(
            "Изменить длительность раунда",
            f"tournament/start_new/edit_round_duration/{settings.to_data()}",
        ).inline()
    )
    keyboard.add(
        Button(
            "Изменить количество Nightmare матчей",
            f"tournament/start_new/edit_nightmare_matches/{settings.to_data()}",
        ).inline()
    )
    keyboard.add(
        Button(
            "Изменить количество Dangerous матчей",
            f"tournament/start_new/edit_dangerous_matches/{settings.to_data()}",
        ).inline()
    )
    keyboard.add(
        Button(
            "Изменить элементные слабости на поле",
            f"tournament/start_new/edit_element_effect_map/{settings.to_data()}",
        ).inline()
    )
    keyboard.add(Button("Отмена", "tournament").inline())
    return keyboard


def offer_to_start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    settings = TournamentSettings.get_default_tournament_settings()
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings,
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=tournament_start_keyboard(settings),
    )


def get_tournament_welcome_message(settings: TournamentSettings) -> str:
    return dedent(
        """
        *Здравствуйте! Здравствуйте! Здравствуйте!*
        
    
        Счастливых вам голодных игр.
        И пусть удача всегда будет с вами.
        """
    )


def start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    settings_data = cb_query.data.removeprefix("tournament/start_new/confirmed/")
    settings = TournamentSettings.from_data(settings_data)
    tournament_manager.start_tournament(settings)
    bot.send_message(
        chat_id=int(getconf("CHAT_ID")),
        text=get_tournament_welcome_message(settings),
        message_thread_id=int(getconf("TOURNAMENT_THREAD_ID")),
    )


def edit_element_effect_map(cb_query: CallbackQuery, bot: TeleBot):
    data = cb_query.data.split("/")
    value = data[3]
    settings = TournamentSettings.from_data("/".join(data[4:]))
    settings.element_effect_map_disabled = value == "off"
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings,
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_param(
    message: Message, bot: TeleBot, param_to_update: str, settings: TournamentSettings
):
    if not message.text.isdigit():
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            Button("Отменить изменение параметра", "tournament/start_new").inline()
        )
        bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат нового значения.\nЗначение может быть только числом.\nПовторите еще раз",
            reply_markup=keyboard,
        )
        bot.register_next_step_handler(
            message, edit_tournament_param, bot, param_to_update, settings
        )
    new_value = int(message.text)
    if param_to_update == "rounds_number":
        settings.rounds_number = new_value
    elif param_to_update == "round_duration_hours":
        settings.round_duration_hours = new_value
    elif param_to_update == "nightmare_matches":
        settings.nightmare_matches = new_value
    elif param_to_update == "dangerous_matches":
        settings.dangerous_matches = new_value

    bot.send_message(
        chat_id=message.chat.id,
        text="*Настройки турнира:*\n" + str(settings),
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_settings(cb_query: CallbackQuery, bot: TeleBot):
    data = cb_query.data.split("/")
    param_to_update = data[2].removeprefix("edit_")
    settings = TournamentSettings.from_data("/".join(data[3:]))
    if param_to_update == "element_effect_map":
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            Button(
                "Включить",
                f"tournament/start_new/edit_element_effect_map/on/{settings.to_data()}",
            ).inline()
        )
        keyboard.add(
            Button(
                "Выключить",
                f"tournament/start_new/edit_element_effect_map/off/{settings.to_data()}",
            ).inline()
        )
        keyboard.add(
            Button("Отменить изменение параметра", "tournament/start_new").inline()
        )
        bot.send_message(
            chat_id=cb_query.message.chat.id,
            text=f"Введите новое значение для {param_to_update}",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            Button("Отменить изменение параметра", "tournament/start_new").inline()
        )
        bot.send_message(
            chat_id=cb_query.message.chat.id,
            text=f"Введите новое значение для {param_to_update}",
            reply_markup=keyboard,
        )
        bot.register_next_step_handler(
            cb_query.message, edit_tournament_param, bot, param_to_update, settings
        )


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
        tournament_main_menu,
        func=empty_filter,
        button="tournament",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        offer_to_start_new_tournament,
        func=empty_filter,
        button="tournament/start_new",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        start_new_tournament,
        func=empty_filter,
        button=f"tournament/start_new/confirmed/{TournamentSettings.data_regexp_repr()}",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_element_effect_map,
        func=empty_filter,
        button=f"tournament/start_new/edit_element_effect_map/[on|off]/{TournamentSettings.data_regexp_repr()}",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_tournament_settings,
        func=empty_filter,
        button=f"tournament/start_new/edit_\w+/{TournamentSettings.data_regexp_repr()}",
        is_private=True,
        pass_bot=True,
    )
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
