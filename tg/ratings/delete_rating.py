from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from db.ratings import ratings_db
from tg.utils import Button, empty_filter


class DelRatingStates(StatesGroup):
    player_data = State()
    confirmed = State()


def delete_rating_options(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for player in ratings_db.get_ratings():
        button = Button(
            f"{player.tg_username}: {player.nmd_username}",
            f"{player.tg_username}",
        )
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())
    bot.set_state(cb_query.from_user.id, DelRatingStates.player_data)

    bot.edit_message_text(
        text="Выберите игрока для удаления из списка рейтингов",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def delete_rating_confirmation(cb_query: CallbackQuery, bot: TeleBot):
    tg_username = cb_query.data
    nmd_username = ratings_db.get_rating(tg_username).nmd_username

    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"approved/{tg_username}").inline())
    keyboard.row(Button("Нет", "ratings").inline())
    bot.set_state(cb_query.from_user.id, DelRatingStates.confirmed)

    bot.edit_message_text(
        text="Вы уверены что хотите удалить игрока "
        + f"{tg_username} \({nmd_username}\)"
        + " из списка рейтингов\?",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def delete_rating_approved(cb_query: CallbackQuery, bot: TeleBot):
    tg_username = int(cb_query.data.split("/")[-1])
    ratings_db.delete_rating(tg_username)
    bot.delete_state(cb_query.from_user.id)

    bot.send_message(
        chat_id=cb_query.message.chat.id,
        text=f"Игрок {tg_username} удален из списка рейтингов",
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        delete_rating_options,
        func=empty_filter,
        button="ratings/delete_rating",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        delete_rating_confirmation,
        func=empty_filter,
        state=DelRatingStates.player_data,
        button="\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        delete_rating_approved,
        func=empty_filter,
        state=DelRatingStates.confirmed,
        button="approved/\w+",
        is_private=True,
        pass_bot=True,
    )
