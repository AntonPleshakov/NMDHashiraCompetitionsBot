import os

import telebot

import db.logs
import db.ratings
from config.config import config, MODE

bot = telebot.TeleBot(config[MODE]["TOKEN"])

tournament_commands_list = ["create_tournament", "register", "get_registered_users"]
rating_commands_list = ["update_attack", "get_rating_list"]
settings_commands_list = ["show_settings", "update_settings"]


@bot.message_handler(commands=["start", "help"])
def start_mes(message):
    bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name}")


@bot.message_handler(commands=["upload_logs"])
def upload_logs(message):
    logs_db = db.logs.Logs()
    logs_db.upload_log_file(os.path.abspath(os.fspath(config[MODE]["LOG_FILE_NAME"])))


@bot.message_handler(commands=["add_user_rating"])
def add_rating(message):
    try:
        ratings_db = db.ratings.Rating()
        ratings_db.add_user_rating(message.from_user.username)
        bot.reply_to(message, "Поздравляю, вы успешно добавлены в рейтинг лист")
    except db.ratings.UsernameAlreadyExistsError:
        bot.reply_to(message, "Ваш никнейм уже есть в рейтинг листе")


if __name__ == "__main__":
    bot.polling()
