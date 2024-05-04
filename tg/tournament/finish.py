from config.config import getconf
from main import bot
from tournament.tournament_manager import tournament_manager


def announce_tournament_end():
    chat_id = int(getconf("CHAT_ID"))
    message_thread_id = int(getconf("TOURNAMENT_THREAD_ID"))
    settings = tournament_manager.tournament.db.settings
    bot.delete_message(chat_id, settings.registration_list_message_id.value)
    bot.send_message(
        chat_id, "Поздравляю с завершением турнира", message_thread_id=message_thread_id
    )
