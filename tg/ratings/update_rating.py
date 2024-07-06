from telebot import TeleBot
from telebot.handler_backends import StatesGroup, State
from telebot.types import CallbackQuery, InlineKeyboardMarkup, Message

from db.ratings import ratings_db, Rating
from logger.NMDLogger import nmd_logger
from tg.utils import Button, empty_filter, get_ids


class UpdateRatingStates(StatesGroup):
    player = State()
    parameter = State()
    new_value = State()


def update_rating_chose_player(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info("Options to update rating")
    keyboard = InlineKeyboardMarkup(row_width=1)
    for player in ratings_db.get_ratings():
        button = Button(
            f"{player.tg_username.value}: {player.nmd_username.value}",
            f"{player.tg_id.value}",
        )
        keyboard.add(button.inline())
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.set_state(user_id, UpdateRatingStates.player)
    bot.edit_message_text(
        text="Выберите игрока для редактирования рейтинга",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def update_rating_parameters(cb_query: CallbackQuery, bot: TeleBot):
    tg_id = cb_query.data
    player = ratings_db.get_rating(tg_id)
    nmd_logger.info(f"Admin chose {player.tg_username} rating to update")

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button(f"{player.rating.view}", f"rating").inline())
    keyboard.add(Button(f"{player.deviation.view}", f"deviation").inline())
    keyboard.add(Button("Назад в Рейтинг лист", "ratings").inline())

    user_id, chat_id, message_id = get_ids(cb_query)
    bot.add_data(user_id, tg_id=tg_id)
    bot.set_state(user_id, UpdateRatingStates.parameter)

    text = f"Выбран игрок {player.tg_username} ({player.nmd_username}):\n"
    for param in player.params().values():
        text += f"{param.view}: {param.value_repr()}\n"

    bot.edit_message_text(
        text=text,
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=keyboard,
    )


def update_rating_enter_value(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"Offer to update {cb_query.data}")
    param_to_update = cb_query.data

    user_id, chat_id, _ = get_ids(cb_query)
    bot.send_message(
        chat_id=chat_id,
        text=f"Введите новое значение для параметра '{Rating().params()[param_to_update].view}'",
    )
    bot.add_data(user_id, param_to_update=param_to_update)
    bot.set_state(user_id, UpdateRatingStates.new_value)


def update_player_parameter(message: Message, bot: TeleBot):
    nmd_logger.info(f"New value for param = {message.text}")
    user_id = message.from_user.id
    with bot.retrieve_data(user_id) as data:
        tg_id = data["tg_id"]
        param_to_update = data["param_to_update"]
    bot.delete_state(user_id)

    new_value = message.text
    player = ratings_db.get_rating(tg_id)
    player.set_value(param_to_update, new_value)
    ratings_db.update_user_rating(tg_id, player)
    bot.reply_to(message, "Параметр успешно обновлен")


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
        state=UpdateRatingStates.player,
        button=r"\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_callback_query_handler(
        update_rating_enter_value,
        func=empty_filter,
        state=UpdateRatingStates.parameter,
        button=r"\w+",
        is_private=True,
        pass_bot=True,
    )
    bot.register_message_handler(
        update_player_parameter,
        chat_types=["private"],
        pass_bot=True,
        state=UpdateRatingStates.new_value,
    )
