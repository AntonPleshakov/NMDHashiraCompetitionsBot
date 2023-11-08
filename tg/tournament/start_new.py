from textwrap import dedent

from telebot import TeleBot, formatting
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message

from config.config import getconf
from tg.utils import Button, empty_filter
from tournament.tournament_manager import tournament_manager
from tournament.tournament_settings import TournamentSettings


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
        text="*Настройки турнира:*\n" + str(settings),
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=tournament_start_keyboard(settings),
    )


def get_tournament_welcome_message(settings: TournamentSettings) -> str:
    return dedent(
        """
        *Здравствуйте\! Здравствуйте\! Здравствуйте\!*


        Счастливых вам голодных игр\.
        И пусть удача всегда будет с вами\.
        """
    )


def start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    settings_data = cb_query.data[len("tournament/start_new/confirmed/") :]
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
        text="*Настройки турнира:*\n" + str(settings),
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
            text="Неверный формат нового значения\.\nЗначение может быть только числом\.\nПовторите еще раз",
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
    param_to_update = data[2][len("edit_") :]
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
            text=f"Введите новое значение для {formatting.escape_markdown(param_to_update)}",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            Button("Отменить изменение параметра", "tournament/start_new").inline()
        )
        bot.send_message(
            chat_id=cb_query.message.chat.id,
            text=f"Введите новое значение для {formatting.escape_markdown(param_to_update)}",
            reply_markup=keyboard,
        )
        bot.register_next_step_handler(
            cb_query.message, edit_tournament_param, bot, param_to_update, settings
        )


def register_handlers(bot: TeleBot):
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
        button=f"tournament/start_new/edit_element_effect_map/(on|off)/{TournamentSettings.data_regexp_repr()}",
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
