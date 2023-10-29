import telebot

import db.ratings_db
from tournament.player import Player


def add_rating(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    try:
        ratings_db = db.ratings_db.RatingsDB()
        ratings_db.add_user_rating(Player(message.from_user.username))
        bot.reply_to(message, "Поздравляю, вы успешно добавлены в рейтинг лист")
        return True
    except db.ratings_db.UsernameAlreadyExistsError:
        bot.reply_to(message, "Ваш никнейм уже есть в рейтинг листе")
        return False


RATINGS_MENU = {"add_rating": add_rating}
