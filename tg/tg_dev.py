import os

import telebot

import db.gapi.gdrive_manager
from config.config import getconf, reset_config


def upload_logs(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    try:
        logs_db = db.gapi.gdrive_manager.GDriveManager()
        logs_db.upload_file(os.path.abspath(os.fspath(getconf("LOG_FILE_NAME"))))
        bot.reply_to(message, "Готово")
        return True
    except FileNotFoundError:
        bot.reply_to(message, "Лог файл еще не создан")
        return False


def update_config(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    files_db = db.gapi.gdrive_manager.GDriveManager()
    files_db.download_file("config.ini", "config/config.ini")
    reset_config("config/config.ini")
    bot.reply_to(message, "Конфигурационный файл обновлен")
    return True


DEV_MENU = {"upload_logs": upload_logs, "update_config": update_config}
