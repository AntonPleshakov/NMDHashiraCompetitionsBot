from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, Message

import tg.common.settings
from db.global_settings import settings_db
from tg import common
from tg.utils import empty_filter, Button

HOME_BTN = Button("Назад в меню", "home").inline()


class GlobalSettingsStates(StatesGroup):
    settings = State()
    edit_param = State()
    new_value = State()


def edit_tournament_settings(cb_query: CallbackQuery, bot: TeleBot):
    common.settings.settings_main_menu(
        cb_query, settings_db.settings, GlobalSettingsStates.settings, HOME_BTN, bot
    )


def offer_to_edit_param(cb_query: CallbackQuery, bot: TeleBot):
    cancel_button = Button("Отменить изменение параметра", "global_settings").inline()
    common.settings.offer_to_edit_param(
        cb_query, GlobalSettingsStates.new_value, cancel_button, bot
    )


def edit_bool_param(cb_query: CallbackQuery, bot: TeleBot):
    common.settings.edit_bool_param(
        cb_query, GlobalSettingsStates.settings, HOME_BTN, bot
    )
    with bot.retrieve_data(cb_query.from_user.id) as data:
        settings = data["settings"]
        settings_db.settings = settings


def edit_int_param(message: Message, bot: TeleBot):
    common.settings.edit_int_param(
        message, GlobalSettingsStates.settings, HOME_BTN, bot
    )
    with bot.retrieve_data(message.from_user.id) as data:
        settings = data["settings"]
        settings_db.settings = settings


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        edit_tournament_settings,
        func=empty_filter,
        button="global_settings",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        offer_to_edit_param,
        func=empty_filter,
        state=GlobalSettingsStates.settings,
        button=f"\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_bool_param,
        func=empty_filter,
        state=GlobalSettingsStates.new_value,
        button=f"(on|off)",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        edit_int_param,
        chat_types=["private"],
        state=GlobalSettingsStates.new_value,
        pass_bot=True,
    )
