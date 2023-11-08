from telebot import TeleBot
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Message

from db.ratings import ratings_db
from tg.utils import Button, empty_filter
from tournament.player import Player


def ratings_main_menu(cb_query: CallbackQuery, bot: TeleBot):
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Изменить рейтинг", "ratings/update_rating").inline())
    keyboard.add(Button("Удалить рейтинг", "ratings/delete_rating").inline())
    keyboard.add(Button("Назад в меню", "home").inline())

    bot.edit_message_text(
        text="Управление списком рейтингов",
        chat_id=cb_query.message.chat.id,
        message_id=cb_query.message.id,
        reply_markup=keyboard,
    )


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
    player = [
        player
        for player in ratings_db.get_ratings()
        if player.tg_username == tg_username
    ][0]

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
        text += f"{field}: {value}"

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
    ratings = ratings_db.get_ratings()
    player_index = -1
    for i, player in enumerate(ratings):
        if player.tg_username == tg_username:
            player_index = i
            break
    param_index = Player.PLAYER_FIELDS.index(param_to_update)
    player = ratings[player_index]
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
        ratings_main_menu,
        func=empty_filter,
        button="ratings",
        is_private=True,
        pass_bot=True,
    )
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
