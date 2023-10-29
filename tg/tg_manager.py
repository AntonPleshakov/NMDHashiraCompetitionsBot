import typing

import telebot

from db.admins_db import admins_db
from tg.tg_admins import ADMINS_MENU
from tg.tg_dev import DEV_MENU
from tg.tg_ratings import RATINGS_MENU
from tg.tg_tournament import TOURNAMENT_MENU
from tg.tg_utils import button

MAIN_MENU = {
    "admins_button": ADMINS_MENU,
    "ratings_button": RATINGS_MENU,
    "tournament_button": TOURNAMENT_MENU,
    "dev_button": DEV_MENU,
}


# _admins_btn = button("admins_button")
# _ratings_btn = button("ratings_button")
# _tournament_btn = button("tournament_button")
# _dev_btn = button("dev_button")
#
# MAIN_KEYBOARD = telebot.types.InlineKeyboardMarkup(row_width=1)
# MAIN_KEYBOARD.add(*[_admins_btn, _ratings_btn, _tournament_btn, _dev_btn, HOME_BTN])


def process_command(command: str = ""):
    menu = MAIN_MENU
    if command == "home_button":
        command = ""
    if command:
        for cmd in command.split(sep="/"):
            menu = menu[cmd]
    if isinstance(menu, typing.Dict):
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*[button(option, command) for option in menu.keys()])
        if command:
            keyboard.add(button("home_button"))
        return keyboard
    else:
        pass


def get_permissions_denied_message():
    admins_list = [
        f"[{admin.username}](tg://user?id={admin.user_id})"
        for admin in admins_db.get_admins()
    ]
    return (
        "Вы не являетесь администратором\.\n"
        + "Взаимодествие с турниром доступно только в специально выделенных чатах\.\n"
        + "Для доступа к административной части обратитесь к одному из администраторов: "
        + "\, ".join(admins_list)
    )
