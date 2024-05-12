from telebot import TeleBot
from telebot.types import (
    InlineKeyboardMarkup,
    CallbackQuery,
)

from db.admins import admins_db
from tg.admins import add_admin, del_admin
from tg.utils import empty_filter, Button, get_ids


def admins_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    user_id, chat_id, message_id = get_ids(cb_query)
    bot.delete_state(user_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Добавить администратора", "admins/add_admin").inline())
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
    current_admins = admins_db.get_admins()
    text = "Список администраторов:\n"
    for admin in current_admins:
        text = text + f"[{admin.username.value}](tg://user?id={admin.user_id.value})\n"

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
