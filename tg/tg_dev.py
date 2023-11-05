import os

from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

import db.gapi.gdrive_manager
from config.config import getconf, reset_config
from tg.tg_utils import empty_filter, Button


def dev_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Загрузить логи", "dev/upload_logs").inline())
    keyboard.add(Button("Обновить файл конфигураций", "dev/update_config").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Служебные функцие",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def upload_logs(cb_query: CallbackQuery, bot: TeleBot):
    try:
        logs_db = db.gapi.gdrive_manager.GDriveManager()
        logs_db.upload_file(os.path.abspath(os.fspath(getconf("LOG_FILE_NAME"))))
        bot.reply_to(cb_query.message, "Логи успешно загружены")
    except FileNotFoundError:
        bot.reply_to(cb_query.message, "Лог файл отсутствует")


def update_config(cb_query: CallbackQuery, bot: TeleBot):
    files_db = db.gapi.gdrive_manager.GDriveManager()
    files_db.download_file("config.ini", "config/config.ini")
    reset_config("config/config.ini")
    bot.reply_to(cb_query.message, "Конфигурационный файл обновлен")


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
