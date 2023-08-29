import os

import telebot

from ConfigManager import config, MODE
from DBManager import DBManager

bot = telebot.TeleBot(config[MODE]["TOKEN"])

tournament_commands_list = ["create_tournament", "register", "get_registered_users"]
rating_commands_list = ["update_attack", "get_rating_list"]
settings_commands_list = ["show_settings", "update_settings"]


@bot.message_handler(commands=["start", "help"])
def start_mes(message):
    bot.send_message(message.chat.id, f"Hi, {message.from_user.first_name}")


@bot.message_handler(commands=["upload_logs"])
def upload_logs(message):
    db = DBManager()
    db.upload_log_file(os.path.abspath(os.fspath(config[MODE]["LOG_FILE_NAME"])))


if __name__ == "__main__":
    bot.polling()
