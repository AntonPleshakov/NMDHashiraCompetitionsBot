from typing import Dict, Union, Callable

import telebot

from db.admins_db import admins_db
from tg.tg_admins import ADMINS_MENU
from tg.tg_dev import DEV_MENU
from tg.tg_ratings import RATINGS_MENU
from tg.tg_tournament import TOURNAMENT_MENU
from tg.tg_utils import button, BTN_TEXT

MAIN_MENU = {
    "admins_button": ADMINS_MENU,
    "ratings_button": RATINGS_MENU,
    "tournament_button": TOURNAMENT_MENU,
    "dev_button": DEV_MENU,
}


def get_main_menu_keyboard():
    menu = MAIN_MENU
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(*[button(option) for option in menu.keys()])
    return keyboard


def home_command(bot: telebot.TeleBot, message: telebot.types.Message) -> bool:
    keyboard = get_main_menu_keyboard()
    text = "Выберите раздел управления"
    if message.from_user.is_bot:
        bot.edit_message_text(
            text=text,
            chat_id=message.chat.id,
            message_id=message.id,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            chat_id=message.chat.id,
            text=text,
            reply_markup=keyboard,
        )
    return True


def process_command(bot: telebot.TeleBot, callback_query: telebot.types.CallbackQuery):
    next_cmd: Union[
        Dict, Callable[[telebot.TeleBot, telebot.types.CallbackQuery], bool]
    ] = MAIN_MENU
    cmd_path = callback_query.data
    if cmd_path:
        for cmd in cmd_path.split(sep="/"):
            next_cmd = home_command if cmd == "home_button" else next_cmd[cmd]
    if isinstance(next_cmd, Dict):
        keyboard = telebot.types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(*[button(option, cmd_path) for option in next_cmd.keys()])
        if cmd_path:
            keyboard.add(button("home_button"))

        btn_data = callback_query.data.split("/")[-1]
        bot.edit_message_text(
            text=BTN_TEXT[btn_data],
            chat_id=callback_query.message.chat.id,
            message_id=callback_query.message.id,
            reply_markup=keyboard,
        )
    elif callable(next_cmd):
        next_cmd(bot, callback_query.message)


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
