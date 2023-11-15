from textwrap import dedent

from telebot import TeleBot, formatting
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message

from config.config import getconf
from parameters import Param
from parameters.bool_param import BoolParam
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
    for attr_name, param in settings.params().items():
        keyboard.add(
            Button(
                f"Изменить {param.view}",
                f"tournament/start_new/edit_{attr_name.lower()}",
            ).inline()
        )
    keyboard.add(Button("Отмена", "tournament").inline())
    return keyboard


def offer_to_start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    settings = TournamentSettings()
    bot.add_data(cb_query.from_user.id, cb_query.message.chat.id, settings=settings)
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
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
    with bot.retrieve_data(cb_query.from_user.id, cb_query.message.chat.id) as data:
        settings = data.pop("settings")
    tournament_manager.start_tournament(settings)
    bot.send_message(
        chat_id=int(getconf("CHAT_ID")),
        text=get_tournament_welcome_message(settings),
        message_thread_id=int(getconf("TOURNAMENT_THREAD_ID")),
    )


def edit_bool_tournament_param(cb_query: CallbackQuery, bot: TeleBot):
    data = cb_query.data.split("/")
    attr_name = data[2][len("edit_") :]
    value = data[3]
    with bot.retrieve_data(cb_query.from_user.id, cb_query.message.chat.id) as data:
        settings = data["settings"]
        settings.set_value(attr_name, value == "on")
        data["settings"] = settings
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_param(
    message: Message, bot: TeleBot, attr_name: str, settings: TournamentSettings
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
            message, edit_tournament_param, bot, attr_name, settings
        )
    settings.params()[attr_name].set_value(message.text)
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        data["settings"] = settings

    bot.send_message(
        chat_id=message.chat.id,
        text="*Настройки турнира:*\n" + settings.view(),
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_settings(cb_query: CallbackQuery, bot: TeleBot):
    with bot.retrieve_data(cb_query.from_user.id, cb_query.message.chat.id) as data:
        settings = data["settings"]
    data = cb_query.data.split("/")
    attr_name = data[2][len("edit_") :]
    param: Param = settings.params()[attr_name]
    if isinstance(param, BoolParam):
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            Button(
                "Включить",
                f"tournament/start_new/edit_{attr_name}/on",
            ).inline()
        )
        keyboard.add(
            Button(
                "Выключить",
                f"tournament/start_new/edit_{attr_name}/off",
            ).inline()
        )
        keyboard.add(
            Button("Отменить изменение параметра", "tournament/start_new").inline()
        )
        bot.send_message(
            chat_id=cb_query.message.chat.id,
            text=f"Введите новое значение для {formatting.escape_markdown(param.value_repr())}",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(
            Button("Отменить изменение параметра", "tournament/start_new").inline()
        )
        bot.send_message(
            chat_id=cb_query.message.chat.id,
            text=f"Введите новое значение для {formatting.escape_markdown(param.value_repr())}",
            reply_markup=keyboard,
        )
        bot.register_next_step_handler(
            cb_query.message,
            edit_tournament_param,
            bot,
            attr_name,
            settings,
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
        button=f"tournament/start_new/confirmed",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_bool_tournament_param,
        func=empty_filter,
        button=f"tournament/start_new/edit_\w+/(on|off)",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_tournament_settings,
        func=empty_filter,
        button=f"tournament/start_new/edit_\w+",
        is_private=True,
        pass_bot=True,
    )
