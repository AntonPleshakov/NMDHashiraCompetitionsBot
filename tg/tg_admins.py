from typing import Optional

from telebot import TeleBot, types, formatting

from db.admins_db import admins_db, Admin


def send_user_request_message(bot: TeleBot, chat_id: int):
    request_user_btn = types.KeyboardButtonRequestUser(request_id=0, user_is_bot=False)
    button = types.KeyboardButton(
        text="Поделиться пользователем", request_user=request_user_btn
    )
    keyboard = types.ReplyKeyboardMarkup(
        resize_keyboard=True, one_time_keyboard=True
    ).add(button)

    bot.send_message(
        chat_id,
        text=formatting.format_text(
            formatting.escape_markdown(
                "Введите данные пользователя в следующем формате:"
            ),
            formatting.escape_markdown("<Имя пользователя> <ID пользователя>"),
            formatting.escape_markdown(
                "Поделитесь пользователем, нажав на кнопку снизу, если его идентификатор вам не известен"
            ),
        ),
        reply_markup=keyboard,
    )


def check_user_info_str(text: str) -> bool:
    user_info = text.split(" ")
    if len(user_info) != 2:
        return False
    return user_info[1].isdigit()


def confirmation_cmd(message: types.Message, bot: TeleBot, admin: Admin):
    print(message.text)


def get_user_info_cmd(message: types.Message, bot: TeleBot, user_id: Optional[int]):
    if message.user_shared:
        user_id = message.user_shared.user_id
        bot.send_message(
            message.chat.id,
            text=f"ID пользователя\: {user_id}\nВведите имя пользователя",
            reply_markup=types.ReplyKeyboardRemove(),
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
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data="yes_btn")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data="no_btn")
    keyboard = types.InlineKeyboardMarkup().row(yes_btn).row(no_btn)
    bot.register_next_step_handler(
        message, confirmation_cmd, bot, Admin(username=username, user_id=user_id)
    )
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


def add_admin_cmd(bot: TeleBot, message: types.Message) -> bool:
    bot.register_next_step_handler(message, get_user_info_cmd, bot, None)
    send_user_request_message(bot, message.chat.id)
    return True


def del_admin_cmd(bot: TeleBot, message: types.Message) -> bool:
    admin_name = message.text
    admins_db.add_admin(Admin(admin_name, 0))
    return True


ADMINS_MENU = {"add_admin": add_admin_cmd, "del_admin": del_admin_cmd}
