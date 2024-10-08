import datetime
import math
import os
import threading
import time
from textwrap import dedent
from typing import Union, Tuple, List, Optional

from telebot import TeleBot
from telebot.types import (
    InlineKeyboardButton,
    KeyboardButton,
    Message,
    CallbackQuery,
    ReactionType,
    ReactionTypeEmoji,
    InlineKeyboardMarkup,
)

from db.admins import admins_db
from db.ratings import Rating, ratings_db
from db.tournament import TournamentDB
from db.tournament_structures import Match, TournamentSettings, RegistrationRow
from logger.NMDLogger import nmd_logger
from tournament.player import Player


def get_user_link(user_id: int, name: str) -> str:
    return f'<a href="tg://user?id={user_id}">{name}</a>'


def get_permissions_denied_message(user_id: int):
    admins_list = [
        get_user_link(admin.user_id, admin.username) for admin in admins_db.get_admins()
    ]
    return (
        "Вы не являетесь администратором.\n"
        + "Взаимодествие с турниром доступно только в специально выделенных чатах.\n"
        + "Для доступа к административной части обратитесь к одному из администраторов с вашим идентификатором.\n"
        + f"Ваш ID: {user_id}\n"
        + "Список администраторов: "
        + ", ".join(admins_list)
    )


def report_to_admins(bot: TeleBot, message: str):
    nmd_logger.info(f"Report a message to admins:\n{message}")
    for admin in admins_db.get_admins():
        bot.send_message(chat_id=admin.user_id.value, text=message)


def _get_right_suffix(value: int, singular: str, few: str, many: str) -> str:
    if value % 10 == 1 and value % 100 != 11:
        return singular
    elif 2 <= value % 10 <= 4 and not 12 <= value % 100 <= 14:
        return few
    else:
        return many


def _get_days_suffix(value: int) -> str:
    return _get_right_suffix(value, "день", "дня", "дней")


def _get_hour_suffix(value: int) -> str:
    return _get_right_suffix(value, "час", "часа", "часов")


def _get_minute_suffix(value: int) -> str:
    return _get_right_suffix(value, "минута", "минуты", "минут")


def _get_tour_suffix(value: int) -> str:
    return _get_right_suffix(value, "тур", "тура", "туров")


def _create_schedule(settings: TournamentSettings) -> str:
    DATETIME_FORMAT = "%d.%m %H:%M"
    registration_hours = settings.registration_duration_hours.value
    tour_hours = settings.round_duration_hours.value
    tour_minutes = settings.round_duration_minutes.value
    tours = settings.rounds_number.value
    curr_time = settings.tournament_start_date + datetime.timedelta(
        hours=registration_hours
    )

    schedule_rows = []
    for i in range(1, tours + 1):
        schedule_rows.append(f"{curr_time.strftime(DATETIME_FORMAT)} - {i} Тур")
        curr_time += datetime.timedelta(hours=tour_hours, minutes=tour_minutes)

    schedule_rows.append(f"{curr_time.strftime(DATETIME_FORMAT)} - Подведение итогов")

    return "\n        ".join(schedule_rows)  # spaces for correct work of dedent


def _get_admins_usernames() -> str:
    admins = admins_db.get_admins()
    admins_links = []
    for admin in admins:
        admins_links.append(f"{get_user_link(admin.user_id, admin.username)}")
    return " ".join(admins_links)


def _get_author_link() -> str:
    author = admins_db.get_admins()[0]
    return get_user_link(author.user_id, author.username)


def _get_str_duration(hours: int, minutes: int) -> str:
    times: List[str] = []
    days: int = math.floor(hours / 24)
    hours = hours % 24
    if days > 0:
        times.append(f"{days} {_get_days_suffix(days)}")
    if hours > 0:
        times.append(f"{hours} {_get_hour_suffix(hours)}")
    if minutes > 0:
        times.append(f"{minutes} {_get_minute_suffix(minutes)}")
    return " ".join(times)


def _get_tour_duration(settings: TournamentSettings) -> str:
    tour_hours = settings.round_duration_hours.value
    tour_minutes = settings.round_duration_minutes.value
    return _get_str_duration(tour_hours, tour_minutes)


def _get_registration_duration(settings: TournamentSettings) -> str:
    reg_hours = settings.registration_duration_hours.value
    return _get_str_duration(reg_hours, 0)


def get_tournament_welcome_message(
    settings: TournamentSettings, tournament_url: str
) -> str:
    registration_hours = settings.registration_duration_hours.value
    tours = settings.rounds_number.value
    return dedent(
        f"""\
        <b>Приветствую всех на очередном турнире</b>
        Регламент:
        Соревнование проводится по системе Мак-Магона в {tours} {_get_tour_suffix(tours)}
        По результатам турнира рейтинг всех игроков будет пересчитан по формуле Эло с учетом динамического отклонения.
        Вы можете обратиться к автору ({_get_author_link()}) для уточнения деталей по формулам.
        Время на регистрацию - {_get_registration_duration(settings)}.
        Длительность каждого тура - {_get_tour_duration(settings)}.
        
        Расписание:
        {_create_schedule(settings)}
        
        Вам предстоит самостоятельно договариваться о битве и создавать карту в соответствии с турнирной таблицей.
        Все битвы проходят до первой победы.

        Напишите мне лично (боту), если хотите добавить или обновить свой игровой никнейм.

        Результаты битв можно будет зарегистрировать под сообщением соответствующего тура.
        Вам следует зарегистрировать победу, если ваш соперник не смог участвовать.
        Вся информация о турнире доступна по <a href="{tournament_url}">ссылке</a>

        По всем вопросам обращайтесь к администраторам:
        {_get_admins_usernames()}
        """
    )


def get_players_table(players: List[Player]) -> str:
    players_rows = []
    max_columns = [0] * 3
    for i in range(len(players) + 1):
        player = players[i - 1] if i != 0 else None
        row = f"{i}: {player.username}" if i != 0 else "Ник"
        max_columns[0] = max(max_columns[0], len(row))
        max_columns[1] = max(max_columns[1], len(str(player.mm) if i != 0 else "MM"))
        max_columns[2] = max(max_columns[2], len(str(player.sos) if i != 0 else "SOS"))
        players_rows.append(row)
    for i, row in enumerate(players_rows):
        row_len = len(row)
        row += " " * (max_columns[0] - row_len)
        player = players[i - 1] if i > 0 else None
        mm = str(player.mm) if i != 0 else "MM"
        row += "| " + mm + " " * (max_columns[1] - len(mm))
        sos = str(player.sos) if i != 0 else "SOS"
        row += (
            "| "
            + sos
            + " " * (max_columns[2] - len(sos))
            + f"| {player.sodos if i != 0 else "SODOS"}"
        )
        players_rows[i] = row
    players_rows.insert(1, "-" * len(players_rows[0]))

    players_str = "\n        ".join(players_rows)  # spaces for correct work of dedent
    print(players_str)
    return dedent(
        f"""\
        <b>Турнирная таблица:</b>

        <pre>{players_str}</pre>
        """
    )


def get_next_tour_message(pairs: List[Match], tours_number: int) -> str:
    pairs_list = []
    for match in pairs:
        first = get_user_link(match.first_id.value, match.first.value)
        if not match.second.value:
            pairs_list.append(f"{first} - техническая победа")
            continue
        second = get_user_link(match.second_id.value, match.second.value)
        rounds = f"Bo{match.rounds.value}"
        pairs_list.append(
            f"{first} {match.result_str} {second}: {match.map.value} ({rounds})"
        )
    pairs_str = "\n        ".join(pairs_list)  # spaces for correct work of dedent
    print(pairs_list)
    return dedent(
        f"""\
        <b>{tours_number} тур</b>

        Пары:
        {pairs_str}

        После завершения битвы зарегистрируйте результат, нажав на кнопку под этим сообщением.
        """
    )


def get_tournament_end_message(tournament_db: TournamentDB) -> str:
    tournament_url = tournament_db.get_url()
    results = tournament_db.get_final_results()

    winners_links = [
        get_user_link(p.tg_id.value, p.tg_username.value) for p in results[:3]
    ]
    places = ["🥇 Первое", "🥈 Второе", "🥉 Третье"]
    winners_list = []
    for i, winner in enumerate(winners_links):
        if i > len(places):
            break
        winners_list.append(places[i] + " место: " + winner)
    winners_str = "\n        ".join(winners_list)  # spaces for correct work of dedent

    new_ratings_list = []
    for i, result in enumerate(results):
        username = result.nmd_username.value
        if not username:
            username = result.tg_username.value
        new_ratings_list.append(
            f"{i + 1}: {get_user_link(result.tg_id.value, username)} \t | {result.rating}"
        )
    new_ratings_str = "\n        ".join(
        new_ratings_list
    )  # spaces for correct work of dedent

    return dedent(
        f"""\
        Трибуты!

        Наш турнир подошел к концу.
        Вы все проявили невероятную силу, стратегию и волю к победе.
        Пришло время объявить результаты и чествовать наших чемпионов.

        {winners_str}

        Вы показали высший класс в этом турнире, и ваши достижения навсегда останутся в истории наших битв.
        Вся информация о результатах турнира доступна по этой <a href="{tournament_url}">ссылке</a>
        Рейтинги всех участников были зарегистрированы и пересчитаны.
        {new_ratings_str}
        Рейтинг лист доступен по <a href="{ratings_db.get_url()}">ссылке</a>

        Мы благодарим всех участников за их усердие и боевой дух.
        Если у вас есть какие-либо вопросы или предложения, не стесняйтесь обращаться к администраторам.

        Пусть удача всегда будет на вашей стороне, и до встречи на следующем турнире! 🎮🏆

        С уважением,
        Администрация турнира
        """
    )


def get_tournament_end_without_players_message() -> str:
    return dedent(
        """\
        Трибуты!

        К сожалению, наш турнир закончился не успев начаться.
        Будем надеяться что в следующий раз желающих поучаствовать будет больше.

        Если у вас есть какие-либо вопросы или предложения, не стесняйтесь обращаться к администраторам.

        Пусть удача всегда будет на вашей стороне, и до встречи на следующем турнире! 🎮🏆

        С уважением,
        Администрация турнира
        """
    )


def get_ids(message: Union[Message, CallbackQuery]) -> Tuple[int, int, int]:
    user_id = message.from_user.id
    if isinstance(message, CallbackQuery):
        message = message.message
    chat_id = message.chat.id
    message_id = message.id
    return user_id, chat_id, message_id


def get_username(message: Union[Message, CallbackQuery]) -> str:
    user = message.from_user
    if user.username:
        return user.username
    return user.first_name


def get_player_rating_view(player: Union[RegistrationRow, Rating]) -> str:
    return f"{player.tg_username.value}({player.nmd_username.value}): {player.rating.value}"


class Button:
    def __init__(self, descr: str, data: str = ""):
        self.data = data
        self.descr = descr

    def inline(self):
        return InlineKeyboardButton(text=self.descr, callback_data=self.data)

    def reply(self):
        return KeyboardButton(text=self.descr)


def empty_filter(_):
    return True


def get_wait_emoji() -> List[ReactionType]:
    return [ReactionTypeEmoji("✍")]


def get_like_emoji() -> List[ReactionType]:
    return [ReactionTypeEmoji("👍")]


def get_dislike_emoji() -> List[ReactionType]:
    return [ReactionTypeEmoji("👎")]


def main_menu_keyboard():
    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(Button("Администраторы", "admins").inline())
    keyboard.add(Button("Рейтинги", "ratings").inline())
    keyboard.add(Button("Глобальные настройки", "global_settings").inline())
    keyboard.add(Button("Турнир", "tournament").inline())
    keyboard.add(Button("Служебные", "dev").inline())
    keyboard.add(Button("Пользовательские", "users").inline())
    return keyboard


def home(message: Union[Message, CallbackQuery], bot: TeleBot):
    username = get_username(message)
    nmd_logger.info(f"Home for {username}")
    keyboard = main_menu_keyboard()
    text = "Выберите раздел управления"
    user_id, chat_id, message_id = get_ids(message)
    if isinstance(message, CallbackQuery):
        bot.edit_message_text(
            text=text,
            chat_id=chat_id,
            message_id=message_id,
            reply_markup=keyboard,
        )
    else:
        bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=keyboard,
        )
    bot.delete_state(user_id)


class TournamentTimer:
    def __init__(self):
        self._timer: Optional[threading.Timer] = None
        self._started_at = None
        self._interval = None

    def update_timer(self, interval, function, args=None, kwargs=None):
        if os.getenv("MODE", "Release") == "Debug":
            interval = interval / 60  # hours to minutes for debug mode
        self._timer = threading.Timer(interval, function, args, kwargs)
        self._interval = interval
        return self

    def start(self):
        if self._timer:
            self._timer.start()
            self._started_at = time.time()

    def remaining(self) -> int:
        if self._interval is None or self._started_at is None:
            print("Remaining: Timer inactive")
            return -1
        print(
            f"Remaining: timer is active: interval - {self._interval}; now - {time.time()}; started_at - {self._started_at}"
        )
        return self._interval - (time.time() - self._started_at)

    def cancel(self):
        if self._timer:
            self._timer.cancel()
            self._started_at = None


tournament_timer = TournamentTimer()
