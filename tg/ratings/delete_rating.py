from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup

from db.ratings import ratings_db
from tg.utils import Button, empty_filter


def delete_rating_options(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for player in ratings_db.get_ratings():
        button = Button(
            f"{player.tg_username}: {player.nmd_username}",
            f"ratings/delete_rating/{player.tg_username}/{player.nmd_username}",
        )
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())

    bot.edit_message_text(
        text="Выберите игрока для удаления из списка рейтингов",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def delete_rating_confirmation(cb_query: CallbackQuery, bot: TeleBot):
    tg_username = cb_query.data.split("/")[-2]
    nmd_username = cb_query.data.split("/")[-1]

    keyboard = InlineKeyboardMarkup()
    keyboard.row(Button("Да", f"ratings/delete_rating/approved/{tg_username}").inline())
    keyboard.row(Button("Нет", "ratings").inline())
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
        button="ratings/delete_rating/\w+/\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        delete_rating_approved,
        func=empty_filter,
        button="ratings/delete_rating/approved/\w+",
        is_private=True,
        pass_bot=True,
    )
