from typing import Union

from telebot import TeleBot, formatting
from telebot.types import (
    InlineKeyboardMarkup,
    CallbackQuery,
    Message,
    InlineKeyboardButton,
)

from db.global_settings import GlobalSettings
from db.tournament_structures import TournamentSettings
from logger.NMDLogger import nmd_logger
from parameters import Param
from parameters.bool_param import BoolParam
from tg.utils import Button, get_ids


def edit_settings_keyboard(
    settings: Union[TournamentSettings, GlobalSettings],
    back_button: InlineKeyboardButton,
) -> InlineKeyboardMarkup:
    nmd_logger.info("Create keyboard with settings")
    keyboard = InlineKeyboardMarkup(row_width=1)
    for attr_name, param in settings.params().items():
        if attr_name in settings.private_parameters():
            continue
        keyboard.add(
            Button(
                f"Изменить {param.view}",
                f"{attr_name.lower()}",
            ).inline()
        )
    keyboard.add(back_button)
    return keyboard


def settings_main_menu(
    cb_query: CallbackQuery,
    settings: Union[TournamentSettings, GlobalSettings],
    state,
    back_button: InlineKeyboardButton,
    bot: TeleBot,
):
    nmd_logger.info("Settings main menu")
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.set_state(user_id, state)
    bot.add_data(user_id, settings=settings)
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=edit_settings_keyboard(settings, back_button),
    )


def offer_to_edit_param(
    cb_query: CallbackQuery, state, back_button: InlineKeyboardButton, bot: TeleBot
):
    attr_name = cb_query.data
    nmd_logger.info(f"Offer to edit parameter {attr_name}")
    user_id, chat_id, message_id = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
        data["param_to_update"] = attr_name
    bot.set_state(user_id, state)

    param: Param = settings.params()[attr_name]
    keyboard = InlineKeyboardMarkup(row_width=1)
    if isinstance(param, BoolParam):
        keyboard.add(Button("Включить", "on").inline())
        keyboard.add(Button("Выключить", "off").inline())
    keyboard.add(back_button)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Введите новое значение для '{formatting.escape_html(param.view)}'",
        reply_markup=keyboard,
    )


def edit_bool_param(
    cb_query: CallbackQuery, state, back_button: InlineKeyboardButton, bot: TeleBot
):
    value = cb_query.data
    user_id, chat_id, message_id = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
        param_to_update = data["param_to_update"]
        settings.set_value(param_to_update, value == "on")
        data["settings"] = settings
    nmd_logger.info(f"Edit bool param {param_to_update} to {value == "on"}")
    bot.set_state(user_id, state)
    bot.send_message(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=chat_id,
        reply_markup=edit_settings_keyboard(settings, back_button),
    )


def edit_int_param(
    message: Message, state, back_button: InlineKeyboardButton, bot: TeleBot
):
    user_id, chat_id, message_id = get_ids(message)
    if not message.text.isdigit():
        nmd_logger.info(f"Edit param failed, value not digit: {message.text}")
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(back_button)
        bot.send_message(
            chat_id=chat_id,
            text="Неверный формат нового значения.\n"
            "Значение может быть только числом.\n"
            "Повторите еще раз",
            reply_markup=keyboard,
        )

    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
        param_to_update = data["param_to_update"]
        settings.params()[param_to_update].set_value(message.text)
        data["settings"] = settings

    nmd_logger.info(f"Edit param {param_to_update} to {message.text}")
    bot.set_state(user_id, state)
    bot.send_message(
        chat_id=chat_id,
        text="*Настройки турнира:*\n" + settings.view(),
        reply_markup=edit_settings_keyboard(settings, back_button),
    )
