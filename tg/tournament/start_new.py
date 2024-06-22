import threading
from datetime import datetime

from telebot import TeleBot, formatting
from telebot.handler_backends import StatesGroup, State
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message

from config.config import getconf
from db.tournament_structures import TournamentSettings
from parameters import Param
from parameters.bool_param import BoolParam
from tg.utils import Button, empty_filter, get_tournament_welcome_message, get_ids
from tournament.tournament_manager import tournament_manager

CANCEL_BTN = Button("Отменить изменение параметра", "tournament/start_new").inline()
DATETIME_FORMAT = "%d/%m, %H:%M"


def start_new_tournament(bot: TeleBot, settings: TournamentSettings):
    tournament_manager.start_tournament(settings)
    keyboard = InlineKeyboardMarkup()
    keyboard.add(Button("Зарегистрироваться", "tournament/register").inline())
    chat_id = int(getconf("CHAT_ID"))
    message_thread_id = int(getconf("TOURNAMENT_THREAD_ID"))
    message = bot.send_message(
        chat_id=chat_id,
        text=get_tournament_welcome_message(
            settings, tournament_manager.tournament.db.get_url()
        ),
        message_thread_id=message_thread_id,
        reply_markup=keyboard,
    )
    bot.pin_chat_message(chat_id=chat_id, message_id=message.id)


class TournamentStartStates(StatesGroup):
    edit_param = State()
    new_value = State()
    delayed_start = State()


def tournament_start_keyboard(settings: TournamentSettings) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Запустить с выбранными настройками", "start").inline())
    keyboard.add(Button("Запланировать запуск", "delayed_start").inline())
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
    user_id, chat_id, message_id = get_ids(cb_query)
    settings = TournamentSettings.default_settings()
    bot.set_state(user_id, TournamentStartStates.edit_param)
    bot.add_data(user_id, settings=settings)
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_settings(cb_query: CallbackQuery, bot: TeleBot):
    attr_name = cb_query.data
    user_id, chat_id, _ = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
        data["param_to_update"] = attr_name
    bot.set_state(user_id, TournamentStartStates.new_value)

    param: Param = settings.params()[attr_name]
    keyboard = InlineKeyboardMarkup(row_width=1)
    if isinstance(param, BoolParam):
        keyboard.add(Button("Включить", "on").inline())
        keyboard.add(Button("Выключить", "off").inline())
    keyboard.add(CANCEL_BTN)
    bot.send_message(
        chat_id=chat_id,
        text=f"Введите новое значение для '{formatting.escape_markdown(param.view)}'",
        reply_markup=keyboard,
    )


def edit_bool_tournament_param(cb_query: CallbackQuery, bot: TeleBot):
    value = cb_query.data
    user_id, chat_id, message_id = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
        param_to_update = data["param_to_update"]
        settings.set_value(param_to_update, value == "on")
        data["settings"] = settings
    bot.set_state(user_id, TournamentStartStates.edit_param)
    bot.edit_message_text(
        text="*Настройки турнира:*\n" + settings.view(),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=tournament_start_keyboard(settings),
    )


def edit_tournament_param(message: Message, bot: TeleBot):
    user_id, chat_id, _ = get_ids(message)
    if not message.text.isdigit():
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(CANCEL_BTN)
        bot.send_message(
            chat_id=chat_id,
            text="Неверный формат нового значения\.\n"
            "Значение может быть только числом\.\n"
            "Повторите еще раз",
            reply_markup=keyboard,
        )

    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
        param_to_update = data["param_to_update"]
        settings.params()[param_to_update].set_value(message.text)
        data["settings"] = settings

    bot.set_state(user_id, TournamentStartStates.edit_param)
    bot.send_message(
        chat_id=chat_id,
        text="*Настройки турнира:*\n" + settings.view(),
        reply_markup=tournament_start_keyboard(settings),
    )


def delayed_start(cb_query: CallbackQuery, bot: TeleBot):
    user_id, chat_id, _ = get_ids(cb_query)
    bot.set_state(user_id, TournamentStartStates.delayed_start)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(CANCEL_BTN)
    bot.send_message(
        chat_id=chat_id,
        text=f"Введите дату старта в формате ({DATETIME_FORMAT})\n"
        f"Например: ({datetime.now().strftime(DATETIME_FORMAT)})",
        reply_markup=keyboard,
    )


def delayed_start_confirmed(message: Message, bot: TeleBot):
    user_id, chat_id, _ = get_ids(message)
    try:
        start_date = datetime.strptime(message.text, DATETIME_FORMAT)
        start_date = start_date.replace(year=datetime.now().year)
        time_to_start = start_date - datetime.now()
        with bot.retrieve_data(user_id) as data:
            settings = data["settings"]
        bot.delete_state(user_id)

        threading.Timer(
            time_to_start.total_seconds(), start_new_tournament, [bot, settings]
        )
    except Exception as e:
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(CANCEL_BTN)
        bot.send_message(
            chat_id=chat_id,
            text=f"Неудалось обработать сообщение\n{e}\nПовторите еще раз",
            reply_markup=keyboard,
        )


def start_new_tournament_option(cb_query: CallbackQuery, bot: TeleBot):
    user_id = cb_query.from_user.id
    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
    bot.delete_state(user_id)

    start_new_tournament(bot, settings)


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
        delayed_start,
        func=empty_filter,
        state=TournamentStartStates.edit_param,
        button=f"delayed_start",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        delayed_start_confirmed,
        chat_types=["private"],
        state=TournamentStartStates.delayed_start,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        start_new_tournament_option,
        func=empty_filter,
        state=TournamentStartStates.edit_param,
        button=f"start",
        is_private=True,
        pass_bot=True,
    )
