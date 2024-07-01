from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from db.ratings import ratings_db
from logger.NMDLogger import nmd_logger
from tg.utils import Button, empty_filter, get_ids


class DelRatingStates(StatesGroup):
    player_data = State()
    confirmed = State()


def delete_rating_options(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Options to delete rating")
    keyboard = InlineKeyboardMarkup(row_width=1)
    for player in ratings_db.get_ratings():
        button = Button(
            f"{player.tg_username.value}: {player.nmd_username.value}",
            f"{player.tg_id.value}",
        )
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.set_state(user_id, DelRatingStates.player_data)
    bot.edit_message_text(
        text="Выберите игрока для удаления из списка рейтингов",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def delete_rating_confirmation(cb_query: CallbackQuery, bot: TeleBot):
    tg_id = cb_query.data
    rating = ratings_db.get_rating(tg_id)
    nmd_username = rating.nmd_username.value
    tg_username = rating.tg_username.value
    nmd_logger.info(f"Confirmation to delete rating of {tg_username}")

    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"approved/{tg_id}").inline())
    keyboard.row(Button("Нет", "ratings").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.set_state(user_id, DelRatingStates.confirmed)
    bot.edit_message_text(
        text="Вы уверены что хотите удалить игрока "
        + f"{tg_username} \({nmd_username}\)"
        + " из списка рейтингов\?",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def delete_rating_approved(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Confirm user rating delete")
    tg_id = int(cb_query.data.split("/")[-1])
    tg_username = ratings_db.get_rating(tg_id).tg_username.value
    ratings_db.delete_rating(tg_id)

    user_id, chat_id, _ = get_ids(cb_query)
    bot.delete_state(user_id)
    bot.send_message(
        chat_id=chat_id,
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
