import telebot

from db.admins_db import admins_db, Admin


def add_admin_cmd(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    admin_name = message.text
    admins_db.add_admin(Admin(admin_name, 0))
    return True


ADMINS_MENU = {"add_admin": add_admin_cmd}
