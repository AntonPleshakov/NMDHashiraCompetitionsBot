from telebot import TeleBot, formatting
from telebot.handler_backends import State, StatesGroup
from telebot.types import (
    KeyboardButtonRequestUser,
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    InlineKeyboardMarkup,
    CallbackQuery,
)

from db.admins import Admin, admins_db
from logger.NMDLogger import nmd_logger
from tg.utils import Button, empty_filter, get_ids


class AddAdminStates(StatesGroup):
    user_data = State()
    username = State()
    confirmed = State()


def send_user_request_message(bot: TeleBot, chat_id: int, user_id: int):
    nmd_logger.info(f"Send user request message")
    request_user_btn = KeyboardButtonRequestUser(request_id=0, user_is_bot=False)
    button = KeyboardButton(
        text="Поделиться пользователем", request_user=request_user_btn
    )
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button)

    share_userdata_msg = (
        "Введите данные пользователя в следующем формате:\n"
        + "<Имя пользователя> <ID пользователя>\n"
        + "Поделитесь пользователем, нажав на кнопку снизу, если его идентификатор вам не известен"
    )

    bot.send_message(
        chat_id=chat_id,
        text=formatting.escape_markdown(share_userdata_msg),
        reply_markup=keyboard,
    )
    bot.set_state(user_id, AddAdminStates.user_data)


def add_admin(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Add admin for {cb_query.from_user.username}")
    user_id, chat_id, _ = get_ids(cb_query)
    send_user_request_message(bot, chat_id, user_id)


def add_admin_confirmation(message: Message, bot: TeleBot, new_admin: Admin):
    nmd_logger.info(f"Confirmation to add new admin {new_admin.username}")
    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"approved").inline())
    keyboard.row(Button("Нет", "admins").inline())

    user_id, chat_id, message_id = get_ids(message)
    bot.set_state(user_id, AddAdminStates.confirmed)
    bot.add_data(user_id, new_admin=new_admin)

    bot.send_message(
        chat_id=chat_id,
        reply_to_message_id=message_id,
        text="Вы уверены что хотите добавить "
        + f'<a href="tg://user?id={new_admin.user_id}">{new_admin.username}</a>\n'
        + " в качестве администратора?\n"
        + "*Обратите внимание:*\n"
        + "Если имя пользователя в данном сообщении не является ссылкой на профиль, "
        + "то пользователь еще не взаимодействовал с ботом",
        reply_markup=keyboard,
    )


def get_user_data(message: Message, bot: TeleBot):
    nmd_logger.info(f"Get user data: {message.text}")
    user_info = message.text.split(" ")
    if len(user_info) != 2 or not user_info[1].isdigit():
        nmd_logger.info("Wrong format")
        bot.reply_to(message, text="Неверный формат данных пользователя")
        user_id, chat_id, _ = get_ids(message)
        send_user_request_message(bot, chat_id, user_id)
        return

    username = user_info[0]
    new_admin_id = int(user_info[1])
    add_admin_confirmation(message, bot, Admin(username, new_admin_id))


def get_user_id(message: Message, bot: TeleBot):
    nmd_logger.info(f"Get user id: {message.user_shared.user_id}")
    user_id, chat_id, message_id = get_ids(message)
    new_admin_id = message.user_shared.user_id
    bot.add_data(user_id, admin_id=new_admin_id)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Отмена", "admins").inline())
    bot.send_message(
        chat_id,
        text=f"ID пользователя: {new_admin_id}\nВведите имя пользователя",
        reply_markup=keyboard,
    )
    bot.set_state(user_id, AddAdminStates.username)


def get_username(message: Message, bot: TeleBot):
    nmd_logger.info(f"Get username: {message.text}")
    with bot.retrieve_data(message.from_user.id) as data:
        user_id = data.pop("admin_id")
    username = message.text
    add_admin_confirmation(message, bot, Admin(username, user_id))


def add_admin_approved(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Add admin approved")
    user_id, chat_id, _ = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        new_admin = data.pop("new_admin")
    bot.delete_state(user_id)
    admins_db.add_admin(new_admin)
    admin_id = new_admin.user_id
    admin_username = new_admin.username
    bot.send_message(
        chat_id=chat_id,
        text=f'Пользователь <a href="tg://user?id={admin_id}">{admin_username}</a> добавлен в качестве администратора',
    )
    bot.send_message(
        chat_id=admin_id,
        text="Поздравляю! Вам только что выдали права администратора, можете начать с команды /start",
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        add_admin,
        func=empty_filter,
        button="admins/add_admin",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        get_user_data,
        content_types=["text"],
        chat_types=["private"],
        state=AddAdminStates.user_data,
        pass_bot=True,
    )
    bot.register_message_handler(
        get_user_id,
        content_types=["user_shared"],
        chat_types=["private"],
        state=AddAdminStates.user_data,
        pass_bot=True,
    )
    bot.register_message_handler(
        get_username,
        chat_types=["private"],
        state=AddAdminStates.username,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        add_admin_approved,
        func=empty_filter,
        button="approved",
        state=AddAdminStates.confirmed,
        is_private=True,
        pass_bot=True,
    )
