from telebot import TeleBot, formatting
from telebot.handler_backends import State, StatesGroup
from telebot.types import (
    KeyboardButton,
    ReplyKeyboardMarkup,
    Message,
    InlineKeyboardMarkup,
    CallbackQuery,
    KeyboardButtonRequestUsers,
)

from db.admins import Admin, admins_db
from logger.NMDLogger import nmd_logger
from tg.utils import Button, empty_filter, get_ids, home, get_username


class AddAdminStates(StatesGroup):
    share_users = State()
    add_admin = State()


def add_admins(cb_query: CallbackQuery, bot: TeleBot):
    username = get_username(cb_query)
    nmd_logger.info(f"Add admin for {username}")
    user_id, chat_id, message_id = get_ids(cb_query)

    request_user_btn = KeyboardButtonRequestUsers(
        request_id=0,
        user_is_bot=False,
        request_username=True,
    )
    button = KeyboardButton(
        text="Поделиться пользователем", request_users=request_user_btn
    )
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    keyboard.add(button)
    keyboard.add(Button("Отмена", "admins").reply())

    share_userdata_msg = (
        "Поделитесь пользователями, которым вы хотите дать администраторские права"
    )

    bot.delete_message(chat_id, message_id)
    bot.send_message(
        chat_id=chat_id,
        text=formatting.escape_html(share_userdata_msg),
        reply_markup=keyboard,
    )
    bot.set_state(user_id, AddAdminStates.share_users)


def add_admins_confirmation(message: Message, bot: TeleBot):
    new_admins = []
    for user in message.users_shared.users:
        new_admins.append(Admin(user.username, user.user_id))

    nmd_logger.info(
        f"Confirmation to add new admins: {', '.join([a.username.value for a in new_admins])}"
    )
    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"approved").inline())
    keyboard.row(Button("Нет", "admins").inline())

    user_id, chat_id, message_id = get_ids(message)
    bot.set_state(user_id, AddAdminStates.add_admin)
    bot.add_data(user_id, new_admins=new_admins)

    admins_links = [
        f'<a href="tg://user?id={a.user_id}">{a.username}</a>\n' for a in new_admins
    ]

    bot.send_message(
        chat_id=chat_id,
        reply_to_message_id=message_id,
        text="Вы уверены что хотите добавить "
        + f"{', '.join(admins_links)}\n"
        + f" в качестве администратор{'а' if len(admins_links) == 1 else 'ов'}?\n"
        + "*Обратите внимание:*\n"
        + "Если имя пользователя в данном сообщении не является ссылкой на профиль, "
        + "то пользователь еще не взаимодействовал с ботом",
        reply_markup=keyboard,
    )


def add_admins_approved(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Add admin approved")
    user_id, chat_id, message_id = get_ids(cb_query)
    with bot.retrieve_data(user_id) as data:
        new_admins = data.pop("new_admins")
    bot.delete_state(user_id)
    for new_admin in new_admins:
        admins_db.add_admin(new_admin)
        admin_id = new_admin.user_id
        admin_username = new_admin.username
        bot.answer_callback_query(
            cb_query.id,
            text=f"Пользователь {admin_username} добавлен в качестве администратора",
        )
        bot.send_message(
            chat_id=admin_id,
            text="Поздравляю! Вам только что выдали права администратора, можете начать с команды /start",
        )
    home(cb_query, bot)


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        add_admins,
        func=empty_filter,
        button="admins/add_admins",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        add_admins_confirmation,
        content_types=["users_shared"],
        chat_types=["private"],
        state=AddAdminStates.share_users,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        add_admins_approved,
        func=empty_filter,
        button="approved",
        state=AddAdminStates.add_admin,
        is_private=True,
        pass_bot=True,
    )
