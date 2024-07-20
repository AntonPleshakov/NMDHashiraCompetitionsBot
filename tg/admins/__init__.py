from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    CallbackQuery,
)

from db.admins import admins_db
from logger.NMDLogger import nmd_logger
from tg.admins import add_admin, del_admin
from tg.utils import empty_filter, Button, get_ids, get_username, get_user_link


def admins_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    username = get_username(cb_query)
    nmd_logger.info(f"Admins main menu for {username}")
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.delete_state(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Добавить администраторов", "admins/add_admins").inline())
    keyboard.add(Button("Удалить администратора", "admins/del_admin").inline())
    keyboard.add(Button("Список администраторов", "admins/admins_list").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление администраторами",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def admins_list(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Admins list")
    current_admins = admins_db.get_admins()
    text = "Список администраторов:\n"
    admins_str = []
    for admin in current_admins:
        admins_str.append(get_user_link(admin.user_id.value, admin.username.value))
    text += "\n".join(admins_str)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Назад в Администраторы", "admins").inline())

    _, chat_id, message_id = get_ids(cb_query)
    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        admins_main_menu,
        func=empty_filter,
        button="admins",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        admins_list,
        func=empty_filter,
        button="admins/admins_list",
        is_private=True,
        pass_bot=True,
    )

    add_admin.register_handlers(bot)
    del_admin.register_handlers(bot)
