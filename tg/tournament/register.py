from telebot import TeleBot
from telebot.types import CallbackQuery

from db.global_settings import settings_db
from db.ratings import ratings_db, Rating
from logger.NMDLogger import nmd_logger
from nmd_exceptions import PlayerNotFoundError, TournamentStartedError
from tg.utils import empty_filter, get_ids
from tournament.player import Player
from tournament.tournament_manager import tournament_manager


def offer_to_add_info(tg_id: int, bot: TeleBot):
    nmd_logger.info("Send offer to set nmd username")
    bot.send_message(
        chat_id=tg_id,
        text="Для комфортного взаимодействия между игроками рекомендуется указать свой игровой никнейм.\n"
        "Вы можете написать его здесь и отредактировать в любое время.",
    )


def get_registration_list_message() -> str:
    players = tournament_manager.tournament.db.get_registered_players()
    message = "<b>Список зарегистрировавшихся:</b>\n"
    for player in players:
        tg_username = player.tg_username.value
        tg_id = player.tg_id.value_repr()
        nmd_username = player.nmd_username.value
        rating = player.rating.value_repr()
        message = message + f'<a href="tg://user?id={tg_id}">{tg_username}</a>'
        if nmd_username:
            message = message + f" ({nmd_username})"
        message = message + f": Рейтинг {rating}\n"
    return message


def add_or_update_registration_list(bot: TeleBot, add: bool = True):
    chat_id = settings_db.settings.chat_id.value
    message_thread_id = settings_db.settings.tournament_thread_id.value
    settings = tournament_manager.tournament.db.settings

    if settings.registration_list_message_id:
        nmd_logger.info("Update registration list message")
        bot.edit_message_text(
            message_id=settings.registration_list_message_id.value,
            chat_id=chat_id,
            text=get_registration_list_message(),
        )
    elif add:
        nmd_logger.info("Create registration list message")
        message = bot.send_message(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            text=get_registration_list_message(),
        )
        settings.registration_list_message_id.value = message.id


def register(cb_query: CallbackQuery, bot: TeleBot):
    nmd_logger.info(f"User {cb_query.from_user.username} wants to be registered")
    user_id, chat_id, message_id = get_ids(cb_query)
    username = cb_query.from_user.username

    rating = ratings_db.get_rating(user_id)
    if not rating:
        nmd_logger.info(f"No rating for user {cb_query.from_user.username}, create new")
        new_rating = Rating.default(user_id)
        new_rating.tg_username.value = username
        ratings_db.add_user_rating(new_rating)
        offer_to_add_info(user_id, bot)

    player = Player(user_id, rating.rating.value)
    try:
        tournament_manager.tournament.add_player(player)
        add_or_update_registration_list(bot)
        bot.answer_callback_query(message_id, text="Вы зарегистрированы")
    except TournamentStartedError:
        nmd_logger.warning(
            f"User {cb_query.from_user.username} pressed 'register' but tournament started"
        )
        bot.answer_callback_query(
            message_id, text="Турнир уже начался, регистрация закрыта", show_alert=True
        )
    except PlayerNotFoundError:
        nmd_logger.warning(f"Rating not found for player {cb_query.from_user.username}")
        bot.answer_callback_query(
            message_id,
            text="Мы не смогли создать вам рейтинг. Попробуйте снова или обратитесь к администратору",
            show_alert=True,
        )


def register_handlers(bot: TeleBot):
    bot.register_callback_query_handler(
        register,
        func=empty_filter,
        button="tournament/register",
        is_private=False,
        pass_bot=True,
    )
