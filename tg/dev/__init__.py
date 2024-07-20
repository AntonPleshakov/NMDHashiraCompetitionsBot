import os

from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

import db.gapi.gdrive_manager
from config.config import getconf, reset_config
from db.admins import admins_db
from db.ratings import ratings_db
from logger.NMDLogger import nmd_logger
from nmd_exceptions import TournamentNotStartedError
from tg.tournament.register import add_or_update_registration_list
from tg.utils import empty_filter, Button, get_ids, get_username
from tournament.tournament_manager import tournament_manager


def dev_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    username = get_username(cb_query)
    nmd_logger.info(f"Dev main menu for {username}")
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Загрузить логи", "dev/upload_logs").inline())
    keyboard.add(Button("Обновить файл конфигураций", "dev/update_config").inline())
    keyboard.add(Button("Обновить администраторов", "dev/fetch_admins").inline())
    keyboard.add(Button("Обновить рейтинг лист", "dev/fetch_ratings").inline())
    keyboard.add(Button("Обновить турнирные таблицы", "dev/fetch_tournament").inline())
    keyboard.add(
        Button(
            "Обновить сообщение с зарегистрированными игроками",
            "dev/update_reg_message",
        ).inline()
    )
    keyboard.add(Button("Назад в меню", "home").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.edit_message_text(
        text="Служебные функции",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def upload_logs(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Update logs")
    try:
        logs_db = db.gapi.gdrive_manager.GDriveManager()
        logs_db.upload_file(os.path.abspath(os.fspath(getconf("LOG_FILE_NAME"))))
        bot.answer_callback_query(cb_query.id, "Логи успешно загружены")
    except FileNotFoundError:
        nmd_logger.exception("File not found")
        bot.answer_callback_query(cb_query.id, "Лог файл отсутствует")


def update_config(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Update config")
    files_db = db.gapi.gdrive_manager.GDriveManager()
    files_db.download_file("config.ini", "config/config.ini")
    reset_config("config/config.ini")
    bot.answer_callback_query(cb_query.id, "Конфигурационный файл обновлен")


def fetch_admins(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Fetch admins")
    admins_db.fetch_admins()
    bot.answer_callback_query(cb_query.id, "Администраторы обновлены")


def fetch_ratings(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Fetch ratings")
    ratings_db.fetch_ratings()
    bot.answer_callback_query(cb_query.id, "Рейтинг лист обновлен")


def fetch_tournament(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Fetch ratings")
    try:
        tournament_manager.tournament.db.fetch()
        bot.answer_callback_query(cb_query.id, "Турнирные таблицы обновлены")
    except TournamentNotStartedError:
        bot.answer_callback_query(cb_query.id, "Нет турнирной таблицы")


def update_reg_message(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Update reg message")
    add_or_update_registration_list(bot, False)
    bot.answer_callback_query(cb_query.id, "Сообщение обновлено")


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        dev_main_menu,
        func=empty_filter,
        button="dev",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        upload_logs,
        func=empty_filter,
        button="dev/upload_logs",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_config,
        func=empty_filter,
        button="dev/update_config",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        fetch_admins,
        func=empty_filter,
        button="dev/fetch_admins",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        fetch_ratings,
        func=empty_filter,
        button="dev/fetch_ratings",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        fetch_tournament,
        func=empty_filter,
        button="dev/fetch_tournament",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_reg_message,
        func=empty_filter,
        button="dev/update_reg_message",
        is_private=True,
        pass_bot=True,
    )
