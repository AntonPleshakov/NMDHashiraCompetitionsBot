from typing import List

from telebot import TeleBot
from telebot.types import InlineKeyboardMarkup

from db.global_settings import settings_db
from db.tournament import TournamentDB
from db.tournament_structures import TournamentSettings, Match
from logger.NMDLogger import nmd_logger
from tg.utils import (
    get_tournament_end_message,
    get_tournament_welcome_message,
    Button,
    get_next_tour_message,
    get_tournament_end_without_players_message,
)


def start_new_tournament(
    settings: TournamentSettings, tournament_db: TournamentDB, bot: TeleBot
):
    nmd_logger.info("Start new tournament")
    keyboard = InlineKeyboardMarkup()
    keyboard.add(Button("Зарегистрироваться", "tournament/register").inline())
    chat_id = settings_db.settings.chat_id.value
    message_thread_id = settings_db.settings.tournament_thread_id.value
    message = bot.send_message(
        chat_id=chat_id,
        text=get_tournament_welcome_message(settings, tournament_db.get_url()),
        message_thread_id=message_thread_id,
        reply_markup=keyboard,
    )
    bot.pin_chat_message(chat_id=chat_id, message_id=message.id)


def announce_new_tour(pairs: List[Match], tournament_db: TournamentDB, bot: TeleBot):
    nmd_logger.info("New tour announcement")
    chat_id = settings_db.settings.chat_id.value
    message_thread_id = settings_db.settings.tournament_thread_id.value
    tours_number = tournament_db.get_tours_number()
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Объявить результат", "tournament/apply_result").inline())
    message = bot.send_message(
        chat_id,
        get_next_tour_message(pairs, tours_number),
        reply_markup=keyboard,
        message_thread_id=message_thread_id,
    )
    bot.pin_chat_message(chat_id, message.id)
    tournament_db.settings.last_tour_message_id = message.id


def announce_tournament_end(tournament_db: TournamentDB, bot: TeleBot):
    nmd_logger.info("End tournament announcement")
    chat_id = settings_db.settings.chat_id.value
    message_thread_id = settings_db.settings.tournament_thread_id.value
    bot.send_message(
        chat_id,
        get_tournament_end_message(tournament_db),
        message_thread_id=message_thread_id,
    )


def announce_tournament_end_without_players(tournament_db: TournamentDB, bot: TeleBot):
    nmd_logger.info("End tournament announcement")
    chat_id = settings_db.settings.chat_id.value
    message_thread_id = settings_db.settings.tournament_thread_id.value
    bot.send_message(
        chat_id,
        get_tournament_end_without_players_message(),
        message_thread_id=message_thread_id,
    )
