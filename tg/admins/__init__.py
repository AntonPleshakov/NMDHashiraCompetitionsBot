from typing import Optional

from telebot import TeleBot, formatting
from telebot.types import (
    InlineKeyboardMarkup,
    CallbackQuery,
    KeyboardButtonRequestUser,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
)

from db.admins import admins_db, Admin
from tg.utils import empty_filter, Button


def admins_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Добавить администратора", "admins/add_admin").inline())
    keyboard.add(Button("Удалить администратора", "admins/del_admin").inline())
    keyboard.add(Button("Список администраторов", "admins/admins_list").inline())
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
        chat_id=chat_id,
        text=formatting.escape_markdown(share_userdata_msg),
        reply_markup=keyboard,
    )
    bot.register_next_step_handler_by_chat_id(chat_id, get_user_info_cmd, bot, None)


def check_user_info_str(text: str) -> bool:
    user_info = text.split(" ")
    if len(user_info) != 2:
        return False
    return user_info[1].isdigit()


def add_admin_confirmation(message: Message, bot: TeleBot, new_admin: Admin):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        Button(
            "Да", f"admins/add_admin/approved/{new_admin.username}/{new_admin.user_id}"
        ).inline()
    )
    keyboard.row(Button("Нет", "admins").inline())

    bot.send_message(
        chat_id=message.chat.id,
        reply_to_message_id=message.id,
        text="Вы уверены что хотите добавить "
        + f"[{new_admin.username}](tg://user?id={new_admin.user_id})"
        + " в качестве администратора\?\n"
        + "*Обратите внимание:*\n"
        + "Если имя пользователя в данном сообщении не является ссылкой на профиль, "
        + "то пользователь еще не взаимодействовал с ботом",
        reply_markup=keyboard,
    )


def get_user_info_cmd(message: Message, bot: TeleBot, user_id: Optional[int]):
    if message.user_shared:
        user_id = message.user_shared.user_id
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(Button("Отмена", "admins").inline())
        bot.send_message(
            message.chat.id,
            text=f"ID пользователя\: {user_id}\nВведите имя пользователя",
            reply_markup=keyboard,
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
    add_admin_confirmation(message, bot, Admin(username, user_id))


def add_admin_cmd(cb_query: CallbackQuery, bot: TeleBot):
    send_user_request_message(bot, cb_query.message.chat.id)


def add_admin_approved_cmd(cb_query: CallbackQuery, bot: TeleBot):
    user_id = cb_query.data.split("/")[-1]
    username = cb_query.data.split("/")[-2]
    admins_db.add_admin(Admin(username, int(user_id)))
    bot.send_message(
        chat_id=cb_query.message.chat.id,
        text=f"Пользователь [{username}](tg://user?id={user_id}) добавлен в качестве администратора",
    )
    bot.send_message(
        chat_id=user_id,
        text="Поздравляю\! Вам только что выдали права администратора\, можете начать с команды \/start",
    )


def del_admin_options_cmd(cb_query: CallbackQuery, bot: TeleBot):
    current_admins = admins_db.get_admins()[1:]  # filter main admin
    keyboard = InlineKeyboardMarkup(row_width=1)
    for admin in current_admins:
        button = Button(f"{admin.username}", f"admins/del_admin/{admin.user_id}")
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Администраторы", "admins").inline())

    bot.edit_message_text(
        text="Выберите пользователя для лишения администраторских прав",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def del_admin_confirmation_cmd(cb_query: CallbackQuery, bot: TeleBot):
    admin_id = int(cb_query.data.split("/")[-1])
    admin_name = [
        admin.username for admin in admins_db.get_admins() if admin.user_id == admin_id
    ][0]

    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"admins/del_admin/approved/{admin_id}").inline())
    keyboard.row(Button("Нет", "admins").inline())

    bot.edit_message_text(
        text="Вы уверены что хотите лишить пользователя "
        + f"[{admin_name}](tg://user?id={admin_id})"
        + " администраторских прав\?",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def del_admin_approved_cmd(cb_query: CallbackQuery, bot: TeleBot):
    admin_id = int(cb_query.data.split("/")[-1])
    admin_name = [
        admin.username for admin in admins_db.get_admins() if admin.user_id == admin_id
    ][0]
    admins_db.del_admin(admin_id)

    bot.send_message(
        chat_id=cb_query.message.chat.id,
        text=f"Пользователь [{admin_name}](tg://user?id={admin_id}) лишен администраторских прав",
    )
    bot.send_message(
        chat_id=admin_id,
        text="Сожалею\, но вы только что были лишены администраторских прав",
    )


def admins_list_cmd(cb_query: CallbackQuery, bot: TeleBot):
    current_admins = admins_db.get_admins()
    text = "Список администраторов:\n"
    for admin in current_admins:
        text = text + f"[{admin.username}](tg://user?id={admin.user_id})\n"

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Назад в Администраторы", "admins").inline())

    bot.edit_message_text(
        text=text,
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
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
        add_admin_cmd,
        func=empty_filter,
        button="admins/add_admin",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        add_admin_approved_cmd,
        func=empty_filter,
        button="admins/add_admin/approved/\w+/\d+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        del_admin_options_cmd,
        func=empty_filter,
        button="admins/del_admin",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        del_admin_confirmation_cmd,
        func=empty_filter,
        button="admins/del_admin/\d+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        del_admin_approved_cmd,
        func=empty_filter,
        button="admins/del_admin/approved/\d+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        admins_list_cmd,
        func=empty_filter,
        button="admins/admins_list",
        is_private=True,
        pass_bot=True,
    )
