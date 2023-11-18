import os

from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

import db.gapi.gdrive_manager
from config.config import getconf, reset_config
from db.admins import admins_db
from db.ratings import ratings_db
from tg.utils import empty_filter, Button, get_ids


def dev_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Загрузить логи", "dev/upload_logs").inline())
    keyboard.add(Button("Обновить файл конфигураций", "dev/update_config").inline())
    keyboard.add(Button("Обновить администраторов", "dev/fetch_admins").inline())
    keyboard.add(Button("Обновить рейтинг лист", "dev/fetch_ratings").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.edit_message_text(
        text="Служебные функции",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def upload_logs(cb_query: CallbackQuery, bot: TeleBot):
    chat_id = cb_query.message.chat.id
    try:
        logs_db = db.gapi.gdrive_manager.GDriveManager()
        logs_db.upload_file(os.path.abspath(os.fspath(getconf("LOG_FILE_NAME"))))
        bot.send_message(chat_id, "Логи успешно загружены")
    except FileNotFoundError:
        bot.send_message(chat_id, "Лог файл отсутствует")


def update_config(cb_query: CallbackQuery, bot: TeleBot):
    files_db = db.gapi.gdrive_manager.GDriveManager()
    files_db.download_file("config.ini", "config/config.ini")
    reset_config("config/config.ini")
    bot.send_message(cb_query.message.chat.id, "Конфигурационный файл обновлен")


def fetch_admins(cb_query: CallbackQuery, bot: TeleBot):
    admins_db.fetch_admins()
    bot.send_message(cb_query.message.chat.id, "Администраторы обновлены")


def fetch_ratings(cb_query: CallbackQuery, bot: TeleBot):
    ratings_db.fetch_ratings()
    bot.send_message(cb_query.message.chat.id, "Рейтинг лист обновлен")


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
