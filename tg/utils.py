from textwrap import dedent
from typing import Union, Tuple

from telebot.types import InlineKeyboardButton, KeyboardButton, Message, CallbackQuery

from db.admins import admins_db
from tournament.tournament_settings import TournamentSettings


def get_permissions_denied_message(user_id: int):
    admins_list = [
        f"[{admin.username}](tg://user?id={admin.user_id})"
        for admin in admins_db.get_admins()
    ]
    return (
        "Вы не являетесь администратором\.\n"
        + "Взаимодествие с турниром доступно только в специально выделенных чатах\.\n"
        + "Для доступа к административной части обратитесь к одному из администраторов с вашим идентификатором\.\n"
        + f"Ваш ID\: {user_id}\n"
        + "Список администраторов\: "
        + "\, ".join(admins_list)
    )


def get_tournament_welcome_message(settings: TournamentSettings) -> str:
    return dedent(
        """
        *Здравствуйте\! Здравствуйте\! Здравствуйте\!*


        Счастливых вам голодных игр\.
        И пусть удача всегда будет с вами\.
        """
    )


def get_ids(message: Union[Message, CallbackQuery]) -> Tuple[int, int, int]:
    user_id = message.from_user.id
    if isinstance(message, CallbackQuery):
        message = message.message
    chat_id = message.chat.id
    message_id = message.id
    return user_id, chat_id, message_id


class Button:
    def __init__(self, descr: str, data: str = ""):
        self.data = data
        self.descr = descr

    def inline(self):
        return InlineKeyboardButton(text=self.descr, callback_data=self.data)

    def reply(self):
        return KeyboardButton(text=self.descr)


def empty_filter(_):
    return True
