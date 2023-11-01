from typing import Optional

from telebot import TeleBot, formatting
from telebot.types import (
    InlineKeyboardMarkup,
    CallbackQuery,
    KeyboardButtonRequestUser,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    ReplyKeyboardRemove,
)

from db.admins_db import admins_db, Admin
from tg.tg_utils import empty_filter, Button


def admins_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Добавить администратора", "admins/add_admin").inline())
    keyboard.add(Button("Удалить администратора", "admins/del_admin").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление администраторами",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def send_user_request_message(bot: TeleBot, chat_id: int):
    request_user_btn = KeyboardButtonRequestUser(request_id=0, user_is_bot=False)
    button = KeyboardButton(
        text="Поделиться пользователем", request_user=request_user_btn
    )
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button)

    share_userdata_msg = (
        "Введите данные пользователя в следующем формате:"
        + "<Имя пользователя> <ID пользователя>"
        + "Поделитесь пользователем, нажав на кнопку снизу, если его идентификатор вам не известен"
    )

    bot.send_message(
        chat_id,
        text=formatting.escape_markdown(share_userdata_msg),
        reply_markup=keyboard,
    )
    bot.register_next_step_handler_by_chat_id(chat_id, get_user_info_cmd, bot)


def check_user_info_str(text: str) -> bool:
    user_info = text.split(" ")
    if len(user_info) != 2:
        return False
    return user_info[1].isdigit()


def get_user_info_cmd(message: Message, bot: TeleBot, user_id: Optional[int]):
    if message.user_shared:
        user_id = message.user_shared.user_id
        bot.send_message(
            message.chat.id,
            text=f"ID пользователя\: {user_id}\nВведите имя пользователя",
            reply_markup=ReplyKeyboardRemove(),
        )
        bot.register_next_step_handler(message, get_user_info_cmd, bot, user_id)
        return
    elif user_id:
        username = message.text
    elif check_user_info_str(message.text):
        user_info = message.text.split(" ")
        username = user_info[0]
        user_id = int(user_info[1])
    else:
        bot.register_next_step_handler(message, get_user_info_cmd, bot, None)
        bot.reply_to(message, text="Неверный формат данных пользователя")
        send_user_request_message(bot, message.chat.id)
        return
    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", "admins/add_admin/yes").inline())
    keyboard.row(Button("Нет", "admins/add_admin/no").inline())

    bot.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text="Вы уверены что хотите добавить "
        + formatting.mlink(content=username, url=f"tg://user?id={user_id}")
        + " в качестве администратора\?\n"
        + "*Обратите внимание:*\n"
        + "Если имя пользователя в данном сообщении не является ссылкой на профиль, "
        + "то пользователь еще не взаимодействовал с ботом",
        reply_markup=keyboard,
    )
    bot.register_next_step_handler(
        message, confirmation_cmd, bot, Admin(username=username, user_id=user_id)
    )


def add_admin_cmd(cb_query: CallbackQuery, bot: TeleBot):
    send_user_request_message(bot, cb_query.message.chat.id)
    bot.register_next_step_handler(cb_query.message, get_user_info_cmd, bot)


def del_admin_cmd(cb_query: CallbackQuery, bot: TeleBot):
    admin_name = cb_query.message.text
    admins_db.add_admin(Admin(admin_name, 0))
    return True


def confirmation_cmd(message: Message, bot: TeleBot, admin: Admin):
    print(message.text)


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        admins_main_menu,
        func=empty_filter,
        button="admins",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        add_admin_cmd,
        func=empty_filter,
        button="admins/add_admin",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        del_admin_cmd,
        func=empty_filter,
        button="admins/del_admin",
        is_private=True,
        pass_bot=True,
    )
