from typing import Union

from telebot import TeleBot
from telebot.types import CallbackQuery, Message

from db.ratings import ratings_db
from db.tournament_structures import RegistrationRow
from tg.tournament.register import add_or_update_registration_list
from tg.utils import get_ids
from tournament.tournament_manager import tournament_manager


def users_main_menu(message: Union[Message, CallbackQuery], bot: TeleBot):
    _, chat_id, _ = get_ids(message)
    bot.send_message(
        chat_id=chat_id,
        text="Добро пожаловать в менеджер турниров Hashira\.\n"
        "Для обновления вашего игрового никнейма просто напишите его здесь",
    )


def update_nmd_username(message: Message, bot: TeleBot):
    user_id = message.from_user.id
    new_nmd_username = message.text
    rating = ratings_db.get_rating(user_id)
    rating.nmd_username.set_value(new_nmd_username)
    ratings_db.update_user_rating(user_id, rating)
    tournament_manager.tournament.update_player_info(
        RegistrationRow.from_rating(rating)
    )
    bot.reply_to(message, "Ваш игровой никнейм обновлен")
    add_or_update_registration_list(bot, False)


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        users_main_menu,
        func=lambda cb: ratings_db.get_rating(cb.from_user.id) is not None,
        button="users",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        users_main_menu,
        func=lambda cb: ratings_db.get_rating(cb.from_user.id) is not None,
        commands=["start"],
        chat_types=["private"],
        pass_bot=True,
        is_admin=False,
    )
    bot.register_message_handler(
        update_nmd_username,
        func=lambda cb: ratings_db.get_rating(cb.from_user.id) is not None,
        chat_types=["private"],
        pass_bot=True,
        is_admin=False,
    )
