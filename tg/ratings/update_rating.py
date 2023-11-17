from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Message

from db.ratings import ratings_db
from tg.utils import Button, empty_filter
from tournament.player import Player


def update_rating_chose_player(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    for player in ratings_db.get_ratings():
        button = Button(
            f"{player.tg_username}: {player.nmd_username}",
            f"ratings/update_rating/{player.tg_username}",
        )
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())

    bot.edit_message_text(
        text="Выберите игрока для редактирования рейтинга",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def update_rating_parameters(cb_query: CallbackQuery, bot: TeleBot):
    tg_username = cb_query.data.split("/")[-1]
    player = ratings_db.get_rating(tg_username)

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        Button(
            f"Рейтинг", f"ratings/update_rating/rating/{player.tg_username}"
        ).inline()
    )
    keyboard.add(
        Button(
            f"Отклонение", f"ratings/update_rating/deviation/{player.tg_username}"
        ).inline()
    )
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())

    text = f"Выбран игрок {player.tg_username} \({player.nmd_username}\):\n"
    for field, value in zip(player.PLAYER_FIELDS, player.to_list()):
        text += f"{field}: {value}\n"

    bot.edit_message_text(
        text=text,
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


def update_player_parameter(
    message: Message, tg_username: str, param_to_update: str, bot: TeleBot
):
    new_value = message.text
    player = ratings_db.get_rating(tg_username)
    ratings = ratings_db.get_ratings()
    player_index = ratings.index(player)
    param_index = Player.PLAYER_FIELDS.index(param_to_update)
    raw_player = player.to_list()
    raw_player[param_index] = new_value
    new_player = Player.from_list(raw_player)
    ratings[player_index] = new_player
    ratings_db.update_all_user_ratings(ratings)
    bot.reply_to(message, "Параметр успешно обновлен")


def update_rating_enter_value(cb_query: CallbackQuery, bot: TeleBot):
    tg_username = cb_query.data.split("/")[-1]
    param_to_update = cb_query.data.split("/")[-1]

    bot.send_message(
        chat_id=cb_query.message.chat.id,
        text=f"Введите новое значение для параметра '{param_to_update}'",
    )
    bot.register_next_step_handler_by_chat_id(
        cb_query.message.chat.id,
        update_player_parameter,
        tg_username,
        param_to_update,
        bot,
    )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        update_rating_chose_player,
        func=empty_filter,
        button="ratings/update_rating",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_rating_parameters,
        func=empty_filter,
        button="ratings/update_rating/\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_rating_enter_value,
        func=empty_filter,
        button="ratings/update_rating/\w+/\w+",
        is_private=True,
        pass_bot=True,
    )
