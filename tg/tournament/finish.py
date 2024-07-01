from telebot import TeleBot

from db.global_settings import settings_db
from logger.NMDLogger import nmd_logger
from tg.utils import get_tournament_end_message
from tournament.tournament_manager import tournament_manager


def announce_tournament_end(bot: TeleBot):
    nmd_logger.info("End tournament announcement")
    chat_id = settings_db.settings.chat_id.value
    message_thread_id = settings_db.settings.tournament_thread_id.value
    settings = tournament_manager.tournament.db.settings
    tournament_url = tournament_manager.tournament.db.settings
    results = tournament_manager.tournament.db.get_final_results()
    winners = [player.tg_username.value for player in results][:3]
    bot.delete_message(chat_id, settings.registration_list_message_id.value)
    bot.send_message(
        chat_id,
        get_tournament_end_message(winners, tournament_url),
        message_thread_id=message_thread_id,
    )
