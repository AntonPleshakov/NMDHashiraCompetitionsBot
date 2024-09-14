from typing import Union

from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, Message, InlineKeyboardMarkup

from db.admins import admins_db
from db.ratings import ratings_db
from logger.NMDLogger import nmd_logger
from nmd_exceptions import TournamentNotStartedError, TournamentStartedError
from tg.tournament.register import add_or_update_registration_list
from tg.utils import (
    get_ids,
    Button,
    empty_filter,
    get_like_emoji,
    get_username,
    get_wait_emoji,
)
from tournament.tournament_manager import tournament_manager


class UsersState(StatesGroup):
    users = State()


def users_main_menu(message: Union[Message, CallbackQuery], bot: TeleBot):
    username = get_username(message)
    nmd_logger.info(f"Main menu for users to {username}")
    user_id, chat_id, message_id = get_ids(message)
    keyboard = None
    rating = ratings_db.get_rating(user_id)
    text = (
        "Добро пожаловать в менеджер турниров Hashira.\n"
        + f"Ваш никнейм: {rating.nmd_username.value}\n"
        if rating.nmd_username.value
        else "Ваш игровой никнейм не указан.\n"
        + "Для обновления вашего игрового никнейма просто напишите его здесь"
    )
    if admins_db.is_admin(user_id):
        bot.set_state(user_id, UsersState.users)
        keyboard = InlineKeyboardMarkup(row_width=1)
        keyboard.add(Button("Назад в меню", "home").inline())

    if admins_db.is_admin(user_id):
        bot.edit_message_text(
            chat_id=chat_id,
            message_id=message_id,
            text=text,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
        )


def update_nmd_username(message: Message, bot: TeleBot):
    username = get_username(message)
    nmd_logger.info(f"User {username} wants to update username to {message.text}")
    user_id, chat_id, message_id = get_ids(message)
    bot.set_message_reaction(chat_id, message_id, get_wait_emoji())

    new_nmd_username = message.text
    if admins_db.is_admin(user_id):
        bot.delete_state(user_id)
    try:
        rating = ratings_db.get_rating(user_id)
        if not rating:
            bot.reply_to(
                message, "У вас еще нет рейтинга, подождите начала следующего турнира"
            )
            return
        rating.nmd_username.set_value(new_nmd_username)
        ratings_db.update_user_rating(user_id, rating)
        tournament_manager.tournament.update_player_info(rating)
        bot.set_message_reaction(chat_id, message_id, get_like_emoji())
        add_or_update_registration_list(bot, False)
    except (TournamentNotStartedError, TournamentStartedError) as e:
        nmd_logger.info(f"User {username} got exception {e}")
        pass


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        users_main_menu,
        func=empty_filter,
        button="users",
        is_admin=True,
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
    bot.register_message_handler(
        update_nmd_username,
        func=empty_filter,
        chat_types=["private"],
        state=UsersState.users,
        pass_bot=True,
        is_admin=True,
    )
