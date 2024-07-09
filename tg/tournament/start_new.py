from datetime import datetime

from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import InlineKeyboardMarkup, CallbackQuery, Message

import tg.common.settings
from db.tournament_structures import TournamentSettings
from logger.NMDLogger import nmd_logger
from tg import common
from tg.utils import (
    Button,
    empty_filter,
    get_ids,
    get_like_emoji,
    home,
    tournament_timer,
)
from tournament.tournament_manager import tournament_manager, TournamentManager

MENU_BTN = Button("Назад в турнир", "tournament/start_new").inline()
DATETIME_FORMAT = "%d.%m %H:%M"


class TournamentStartStates(StatesGroup):
    main_menu = State()
    delayed_start = State()
    settings = State()
    edit_param = State()
    new_value = State()


def tournament_start_keyboard() -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Запустить с текущими настройками", "start").inline())
    keyboard.add(Button("Запланировать запуск", "delayed_start").inline())
    keyboard.add(Button("Изменить настройки", "edit_settings").inline())
    keyboard.add(Button("Отмена", "tournament").inline())
    return keyboard


def new_tournament_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Offer to start new tournament for {cb_query.from_user.username}")
    user_id, chat_id, message_id = get_ids(cb_query)
    settings = TournamentSettings.default_settings()
    if bot.current_states.get_data(chat_id, user_id):
        with bot.retrieve_data(user_id) as data:
            if "settings" in data:
                settings = data["settings"]
    bot.set_state(user_id, TournamentStartStates.main_menu)
    bot.add_data(user_id, settings=settings)
    bot.edit_message_text(
        text="<b>Настройки турнира:</b>\n" + settings.view(),
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=tournament_start_keyboard(),
    )


def start_new_tournament_option(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Start tournament immediately")
    user_id, _, _ = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        settings = data["settings"]
    bot.delete_state(user_id)

    bot.answer_callback_query(
        cb_query.id, "Запущен старт турнира, это может занять пару минут"
    )
    tournament_manager.start_tournament(settings)
    home(cb_query, bot)


def delayed_start(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Delayed start")
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.set_state(user_id, TournamentStartStates.delayed_start)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(MENU_BTN)
    bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text=f"Введите дату старта в формате '{DATETIME_FORMAT}'\n"
        f"Например: {datetime.now().strftime(DATETIME_FORMAT)}",
        reply_markup=keyboard,
    )
    bot.add_data(user_id, message_id=message_id)


def delayed_start_confirmed(message: Message, bot: TeleBot):
    nmd_logger.info(f"Delayed start confirmed in {message.text}")
    user_id, chat_id, message_id = get_ids(message)
    try:
        start_date = datetime.strptime(message.text, DATETIME_FORMAT)
        start_date = start_date.replace(year=datetime.now().year)
        time_to_start = start_date - datetime.now()
        with bot.retrieve_data(user_id) as data:
            settings = data["settings"]
        bot.delete_state(user_id)

        tournament_timer.update_timer(
            time_to_start.total_seconds(),
            TournamentManager.start_tournament,
            [tournament_manager, settings],
        ).start()
        nmd_logger.info(
            f"Tournament will start in {time_to_start.total_seconds()} seconds"
        )
        bot.set_message_reaction(chat_id, message_id, get_like_emoji())
        home(message, bot)
    except Exception as e:
        nmd_logger.info("Exception in delayed start")
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(MENU_BTN)
        with bot.retrieve_data(user_id) as data:
            offer_message_id = data["offer_message_id"]
        bot.delete_message(chat_id, message_id)
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=offer_message_id,
            text=f"Неудалось обработать сообщение\n{e}\nПовторите еще раз",
            reply_markup=keyboard,
        )


def edit_tournament_settings(cb_query: CallbackQuery, bot: TeleBot):
    with bot.retrieve_data(cb_query.from_user.id) as data:
        settings = data["settings"]
    common.settings.settings_main_menu(
        cb_query, settings, TournamentStartStates.settings, MENU_BTN, bot
    )


def offer_to_edit_param(cb_query: CallbackQuery, bot: TeleBot):
    cancel_btn = Button("Отменить изменение параметра", "edit_settings").inline()
    common.settings.offer_to_edit_param(
        cb_query, TournamentStartStates.new_value, cancel_btn, bot
    )


def edit_bool_param(cb_query: CallbackQuery, bot: TeleBot):
    common.settings.edit_bool_param(
        cb_query, TournamentStartStates.settings, MENU_BTN, bot
    )


def edit_int_param(message: Message, bot: TeleBot):
    common.settings.edit_int_param(
        message, TournamentStartStates.settings, MENU_BTN, bot
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        new_tournament_main_menu,
        func=empty_filter,
        button="tournament/start_new",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        start_new_tournament_option,
        func=empty_filter,
        state=TournamentStartStates.main_menu,
        button=f"start",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        delayed_start,
        func=empty_filter,
        state=TournamentStartStates.main_menu,
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
        edit_tournament_settings,
        func=empty_filter,
        state=TournamentStartStates.main_menu,
        button="edit_settings",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        offer_to_edit_param,
        func=empty_filter,
        state=TournamentStartStates.settings,
        button=r"\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        edit_bool_param,
        func=empty_filter,
        state=TournamentStartStates.new_value,
        button=r"(on|off)",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        edit_int_param,
        chat_types=["private"],
        state=TournamentStartStates.new_value,
        pass_bot=True,
    )
