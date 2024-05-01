from telebot import TeleBot
from telebot.types import CallbackQuery

from config.config import getconf
from db.ratings import ratings_db, Rating
from nmd_exceptions import PlayerNotFoundError, TournamentStartedError
from tg.utils import empty_filter, get_ids
from tournament.player import Player
from tournament.tournament_manager import tournament_manager


def offer_to_add_info(tg_id: int, bot: TeleBot):
    bot.send_message(
        chat_id=tg_id,
        text="Для комфортного взаимодействия между игроками рекомендуется указать свой игровой никнейм\.\n"
        "Вы можете написать его здесь и отредактировать в любое время\.",
    )


def get_registration_list_message() -> str:
    players = tournament_manager.tournament.db.get_registered_players()
    message = "Список зарегистрировавшихся\:\n"
    for player in players:
        tg_username = player.tg_username.value
        id = str(player.tg_id.value)
        nmd_username = player.nmd_username.value
        rating = player.rating.value
        message = message + f"[{tg_username}](tg://user?id={id})"
        if nmd_username:
            message = message + f" \({nmd_username}\)"
        message = message + f"\: Рейтинг {rating}\n"
    return message


def add_or_update_registration_list(bot: TeleBot, add: bool = True):
    chat_id = int(getconf("CHAT_ID"))
    message_thread_id = int(getconf("TOURNAMENT_THREAD_ID"))
    settings = tournament_manager.tournament.db.settings

    if settings.registration_list_message_id:
        bot.edit_message_text(
            message_id=settings.registration_list_message_id,
            chat_id=chat_id,
            text=get_registration_list_message(),
        )
    elif add:
        message = bot.send_message(
            chat_id=chat_id,
            message_thread_id=message_thread_id,
            text=get_registration_list_message(),
        )
        settings.registration_list_message_id.value = message.id


def register(cb_query: CallbackQuery, bot: TeleBot):
    user_id, chat_id, message_id = get_ids(cb_query)
    username = cb_query.from_user.username

    rating = ratings_db.get_rating(user_id)
    if not rating:
        default_player = Player(user_id)
        new_rating = Rating.from_player(default_player)
        new_rating.tg_username.value = username
        ratings_db.add_user_rating(new_rating)
        offer_to_add_info(user_id, bot)

    player = Player(user_id, rating.rating.value, rating.deviation.value)
    try:
        tournament_manager.tournament.add_player(player)
        add_or_update_registration_list(bot)
        bot.answer_callback_query(message_id, text="Вы зарегистрированы")
    except TournamentStartedError:
        bot.answer_callback_query(
            message_id, text="Турнир уже начался, регистрация закрыта", show_alert=True
        )
    except PlayerNotFoundError:
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
        is_private=True,
        pass_bot=True,
    )
