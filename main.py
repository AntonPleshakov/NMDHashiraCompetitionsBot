import os

import telebot

import db.gdrive_manager
import db.ratings
from config.config import config, MODE

bot = telebot.TeleBot(config[MODE]["TOKEN"])


@bot.message_handler(commands=["start", "help"])
def start_mes(message):
    bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name}")


@bot.message_handler(commands=["upload_logs"])
def upload_logs(message):
    try:
        logs_db = db.gdrive_manager.GDriveManager()
        logs_db.upload_file(os.path.abspath(os.fspath(config[MODE]["LOG_FILE_NAME"])))
        bot.reply_to(message, "Готово")
    except FileNotFoundError:
        bot.reply_to(message, "Лог файл еще не создан")


@bot.message_handler(commands=["add_user_rating"])
def add_rating(message):
    try:
        ratings_db = db.ratings.Rating()
        ratings_db.add_user_rating(message.from_user.username)
        bot.reply_to(message, "Поздравляю, вы успешно добавлены в рейтинг лист")
    except db.ratings.UsernameAlreadyExistsError:
        bot.reply_to(message, "Ваш никнейм уже есть в рейтинг листе")


@bot.message_handler(commands=["update_config"])
def update_config(message):
    files_db = db.gdrive_manager.GDriveManager()
    files_db.download_file("config.ini", "config/config.ini")
    config.read("config/config.ini")
    bot.reply_to(message, "Конфигурационный файл обновлен")


if __name__ == "__main__":
    bot.polling()
