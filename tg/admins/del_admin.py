from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from db.admins import admins_db
from tg.utils import Button, empty_filter, get_ids


class DelAdminStates(StatesGroup):
    admin_id = State()
    confirmed = State()


def del_admin_options(cb_query: CallbackQuery, bot: TeleBot):
    current_admins = admins_db.get_admins()[1:]  # filter main admin
    keyboard = InlineKeyboardMarkup(row_width=1)
    for admin in current_admins:
        button = Button(f"{admin.username}", f"{admin.user_id}")
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Администраторы", "admins").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.edit_message_text(
        text="Выберите пользователя для лишения администраторских прав",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )
    bot.set_state(user_id, DelAdminStates.admin_id)


def del_admin_confirmation(cb_query: CallbackQuery, bot: TeleBot):
    admin_id = int(cb_query.data)
    admin_name = [
        admin.username for admin in admins_db.get_admins() if admin.user_id == admin_id
    ][0]

    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"approved/{admin_id}").inline())
    keyboard.row(Button("Нет", "admins").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.edit_message_text(
        text="Вы уверены что хотите лишить пользователя "
        + f"[{admin_name}](tg://user?id={admin_id})"
        + " администраторских прав\?",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )
    bot.set_state(user_id, DelAdminStates.confirmed)


def del_admin_approved(cb_query: CallbackQuery, bot: TeleBot):
    admin_id = int(cb_query.data.split("/")[-1])
    admin_name = [
        admin.username for admin in admins_db.get_admins() if admin.user_id == admin_id
    ][0]
    admins_db.del_admin(admin_id)

    user_id, chat_id, _ = get_ids(cb_query)
    bot.delete_state(user_id)
    bot.send_message(
        chat_id=chat_id,
        text=f"Пользователь [{admin_name}](tg://user?id={admin_id}) лишен администраторских прав",
    )
    bot.send_message(
        chat_id=admin_id,
        text="Сожалею\, но вы только что были лишены администраторских прав",
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        del_admin_options,
        func=empty_filter,
        button="admins/del_admin",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        del_admin_confirmation,
        func=empty_filter,
        state=DelAdminStates.admin_id,
        button="\d+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        del_admin_approved,
        func=empty_filter,
        state=DelAdminStates.confirmed,
        button="approved/\d+",
        is_private=True,
        pass_bot=True,
    )
