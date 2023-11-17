from telebot import TeleBot, formatting
from telebot.handler_backends import StatesGroup, State
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message

from config.config import getconf
from parameters import Param
from parameters.bool_param import BoolParam
from tg.utils import Button, empty_filter, get_tournament_welcome_message
from tournament.tournament_manager import tournament_manager
from tournament.tournament_settings import TournamentSettings

CANCEL_BTN = Button("Отменить изменение параметра", "tournament/start_new").inline()


class TournamentStartStates(StatesGroup):
    edit_param = State()
    new_value = State()


def tournament_start_keyboard(settings: TournamentSettings) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Запустить с выбранными настройками", "confirmed").inline())
    for attr_name, param in settings.params().items():
        keyboard.add(
            Button(
                f"Изменить {param.view}",
                f"{attr_name.lower()}",
            ).inline()
        )
    keyboard.add(Button("Отмена", "tournament").inline())
    return keyboard


def offer_to_start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    settings = TournamentSettings()
    bot.set_state(cb_query.from_user.id, TournamentStartStates.edit_param)
    bot.add_data(cb_query.from_user.id, settings=settings)
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_settings(cb_query: CallbackQuery, bot: TeleBot):
    attr_name = cb_query.data
    with bot.retrieve_data(cb_query.from_user.id) as data:
        settings = data["settings"]
        data["param_to_update"] = attr_name
    bot.set_state(cb_query.from_user.id, TournamentStartStates.new_value)

    param: Param = settings.params()[attr_name]
    keyboard = InlineKeyboardMarkup(row_width=1)
    if isinstance(param, BoolParam):
        keyboard.add(Button("Включить", "on").inline())
        keyboard.add(Button("Выключить", "off").inline())
    keyboard.add(CANCEL_BTN)
    bot.send_message(
        chat_id=cb_query.message.chat.id,
        text=f"Введите новое значение для {formatting.escape_markdown(param.value_repr())}",
        reply_markup=keyboard,
    )


def edit_bool_tournament_param(cb_query: CallbackQuery, bot: TeleBot):
    value = cb_query.data
    with bot.retrieve_data(cb_query.from_user.id) as data:
        settings = data["settings"]
        param_to_update = data["param_to_update"]
        settings.set_value(param_to_update, value == "on")
        data["settings"] = settings
    bot.set_state(cb_query.from_user.id, TournamentStartStates.edit_param)
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_param(message: Message, bot: TeleBot):
    if not message.text.isdigit():
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(CANCEL_BTN)
        bot.send_message(
            chat_id=message.chat.id,
            text="Неверный формат нового значения\.\n"
            "Значение может быть только числом\.\n"
            "Повторите еще раз",
            reply_markup=keyboard,
        )

    with bot.retrieve_data(message.from_user.id) as data:
        settings = data["settings"]
        param_to_update = data["param_to_update"]
        settings.params()[param_to_update].set_value(message.text)
        data["settings"] = settings

    bot.set_state(message.from_user.id, TournamentStartStates.edit_param)
    bot.send_message(
        chat_id=message.chat.id,
        text="*Настройки турнира:*\n" + settings.view(),
        reply_markup=tournament_start_keyboard(settings),
    )


def start_new_tournament(cb_query: CallbackQuery, bot: TeleBot):
    with bot.retrieve_data(cb_query.from_user.id) as data:
        settings = data["settings"]
    bot.delete_state(cb_query.from_user.id)

    tournament_manager.start_tournament(settings)
    bot.send_message(
        chat_id=int(getconf("CHAT_ID")),
        text=get_tournament_welcome_message(settings),
        message_thread_id=int(getconf("TOURNAMENT_THREAD_ID")),
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
        edit_tournament_settings,
        func=empty_filter,
        state=TournamentStartStates.edit_param,
        button=f"\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_bool_tournament_param,
        func=empty_filter,
        state=TournamentStartStates.new_value,
        button=f"(on|off)",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        edit_tournament_param,
        chat_types=["private"],
        state=TournamentStartStates.new_value,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        start_new_tournament,
        func=empty_filter,
        state=TournamentStartStates.edit_param,
        button=f"confirmed",
        is_private=True,
        pass_bot=True,
    )
