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
from db.tournament_structures import Match, TournamentSettings, RegistrationRow
from logger.NMDLogger import nmd_logger


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


def get_right_suffix(value: int, word_without_suffix: str) -> str:
    if value % 10 == 1 and value % 100 != 11:
        return word_without_suffix
    elif 2 <= value % 10 <= 4 and not 12 <= value % 100 <= 14:
        return word_without_suffix + "а"
    else:
        return word_without_suffix + "ов"


def get_tournament_welcome_message(
    settings: TournamentSettings, tournament_url: str
) -> str:
    registration_hours = settings.registration_duration_hours.value
    tour_hours = settings.round_duration_hours.value
    tours = settings.rounds_number.value
    return dedent(
        f"""\
        <b>Здравствуйте! Здравствуйте! Здравствуйте!</b>
        Приветствую, трибуты!

        Мы рады приветствовать вас на нашем турнире, где вы сможете показать свои навыки и стратегию в битвах.
        Соревнование проводится по системе Мак-Магона в {tours} {get_right_suffix(tours, "тур")}
        По результатам турнира рейтинг всех игроков будет пересчитан по формуле Эло с учетом динамического отклонения.
        Вы можете обратиться к администраторам для уточнения деталей по формулам.
        Время регистрации ограничено – у вас есть всего {registration_hours} {get_right_suffix(registration_hours, "час")}, чтобы заявить о своем участии. ⏳

        Каждый тур будет длиться {tour_hours} {get_right_suffix(tour_hours, "час")}.
        Вам предстоит самостоятельно договариваться о времени битвы и создавать карту в соответствии с турнирной таблицей, которую я буду публиковать в этом чате.
        Все битвы проходят до первой победы.

        📥 Зарегистрироваться на турнир можно, нажав на кнопку под этим сообщением.

        Напишите мне лично, если хотите добавить или обновить свой игровой никнейм.

        Результаты битв можно будет зарегистрировать под сообщением соответствующего тура.
        Зарегистрировать результат достаточно только одному из участников, но мы вас не ограничиваем.
        Вам следует зарегистрировать победу, если ваш соперник не смог участвовать
        Вся информация о турнире, включая список зарегистрировавшихся участников, турнирные таблицы и результаты, будет доступна по этой ссылке: <a href="{tournament_url}">тык</a>

        Если в процессе подготовки к битве или во время турнира у вас возникнут проблемы или вопросы, прошу вас сообщить об этом администраторам.
        Помните, что это первые тестовые запуски, поэтому возможны некоторые трудности.

        Счастливых вам голодных игр.
        И пусть удача всегда будет с вами.
        """
    )


def get_next_tour_message(
    settings: TournamentSettings,
    pairs: List[Match],
    tours_number: int,
    tournament_url: str,
) -> str:
    tour_hours = settings.round_duration_hours.value
    pairs_list = []
    for match in pairs:
        first = get_user_link(match.first_id.value, match.first.value)
        if not match.second.value:
            pairs_list.append(f"{first} - техническая победа")
            continue
        second = get_user_link(match.second_id.value, match.second.value)
        pairs_list.append(f"{first} vs {second}: {match.map.value}")
    pairs_str = "\n        ".join(pairs_list)
    print(pairs_list)
    return dedent(
        f"""\
        Внимание, трибуты!

        Настало время для {tours_number} тура нашего захватывающего турнира.
        Пришло время доказать свою силу и мастерство на арене!

        Напоминаю:
        У вас есть {tour_hours} {get_right_suffix(tour_hours, "час")} на проведение битвы.
        Вся информация о турнире доступна по этой ссылке: <a href="{tournament_url}">тык</a>
        
        Договоритесь с соперником о времени встречи и создайте карту в соответствии со следующей турнирной таблицей:

        {pairs_str}

        После завершения битвы зарегистрируйте результат, нажав на кнопку под этим сообщением.
        Пусть каждый ход приближает вас к победе и славе!

        Помните, что все возникающие вопросы и проблемы должны быть незамедлительно доведены до сведения администраторов.
        Этот турнир – испытание для всех нас, но мы уверены, что вы справитесь.

        И пусть удача всегда будет с вами.
        """
    )


def get_tournament_end_message(winners: List[str], tournament_url: str) -> str:
    places = ["🥇 Первое", "🥈 Второе", "🥉 Третье"]
    winners_list = []
    for i, winner in enumerate(winners):
        if i > len(places):
            break
        winners_list.append(places[i] + " место: " + winner)
    winners_str = "\n        ".join(winners_list)
    return dedent(
        f"""\
        Трибуты!

        Наш турнир подошел к концу.
        Вы все проявили невероятную силу, стратегию и волю к победе.
        Пришло время объявить результаты и чествовать наших чемпионов.

        {winners_str}

        Вы показали высший класс в этом турнире, и ваши достижения навсегда останутся в истории наших битв.
        Вся информация о результатах турнира доступна по этой ссылке: <a href="{tournament_url}">тык</a>
        Рейтинги всех участников были зарегистрированы и пересчитаны. Вы можете посмотреть их здесь: <a href="{ratings_db.get_url()}">тык</a>

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
