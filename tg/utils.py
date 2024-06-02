from textwrap import dedent
from typing import Union, Tuple, List

from telebot.types import InlineKeyboardButton, KeyboardButton, Message, CallbackQuery

from db.admins import admins_db
from db.tournament_structures import Match
from tournament.tournament_settings import TournamentSettings


def get_permissions_denied_message(user_id: int):
    admins_list = [
        f"[{admin.username}](tg://user?id={admin.user_id})"
        for admin in admins_db.get_admins()
    ]
    return (
        "Вы не являетесь администратором\.\n"
        + "Взаимодествие с турниром доступно только в специально выделенных чатах\.\n"
        + "Для доступа к административной части обратитесь к одному из администраторов с вашим идентификатором\.\n"
        + f"Ваш ID\: {user_id}\n"
        + "Список администраторов\: "
        + "\, ".join(admins_list)
    )


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
        f"""
        *Здравствуйте\! Здравствуйте\! Здравствуйте\!*
        Приветствую, трибуты!

        Добро пожаловать на новый турнир, где вы сможете показать свои навыки и стратегию в битвах.
        Соревнование проводится по системе Мак-Магона в {tours} {get_right_suffix(tours, "тур")}
        По результатам турнира рейтинг всех игроков будет пересчитан по формуле Эло с учетом динамического отклонения.
        Время регистрации ограничено – у вас есть всего {registration_hours} {get_right_suffix(registration_hours, "час")}, чтобы заявить о своем участии. ⏳

        Каждый тур будет длиться {tour_hours} {get_right_suffix(tour_hours, "час")}.
        Вам предстоит самостоятельно договариваться о времени битвы и создавать карту в соответствии с турнирной таблицей, которую я буду публиковать в этом чате.

        📥 Зарегистрироваться на турнир можно, нажав на кнопку под этим сообщением.

        После регистрации я свяжусь с вами лично, чтобы уточнить ваш ник в игре, если он мне еще не известен.

        Результаты битв можно будет зарегистрировать под сообщением соответствующего тура.
        Вся информация о турнире, включая список зарегистрировавшихся участников, турнирные таблицы и результаты, будет доступна по этой ссылке: {tournament_url}

        Если в процессе подготовки к битве или во время турнира у вас возникнут проблемы или вопросы, прошу вас сообщить об этом администраторам.
        Помните, что это первые тестовые запуски, поэтому возможны некоторые трудности.

        Счастливых вам голодных игр\.
        И пусть удача всегда будет с вами\.
        """
    )


def get_next_tour_message(
    settings: TournamentSettings, pairs: List[Match], tournament_url: str
) -> str:
    tour_hours = settings.round_duration_hours.value
    pairs_str = ""
    for match in pairs:
        first = f"[{match.first.value}](tg://user?id={match.first_id})"
        second = f"[{match.second.value}](tg://user?id={match.second_id})"
        pairs_str += f"{first} vs {second}"
    return dedent(
        f"""
        Внимание, трибуты!

        Настало время для следующего тура нашего захватывающего турнира.
        Пришло время доказать свою силу и мастерство на арене!

        У вас есть {tour_hours} {get_right_suffix(tour_hours, "час")} на проведение битвы.
        Договоритесь с соперником о времени встречи и создайте карту в соответствии со следующей турнирной таблицей:
        {pairs_str}
        Вся информация о турнире доступна по этой ссылке: {tournament_url}

        После завершения битвы зарегистрируйте результат, нажав на кнопку под этим сообщением.
        Пусть каждый ход приближает вас к победе и славе!

        Помните, что все возникающие вопросы и проблемы должны быть незамедлительно доведены до сведения администраторов.
        Этот турнир – испытание для всех нас, но мы уверены, что вы справитесь.

        Пусть удача будет на вашей стороне! Да начнется битва! 🎮🏆
        """
    )


def get_tournament_end_message(winners: List[str], tournament_url: str) -> str:
    places = ["🥇 Первое", "🥈 Второе", "🥉 Третье"]
    winners_str = ""
    for i, winner in enumerate(winners):
        if i > len(places):
            break
        winners_str += places[i] + " место: " + winner + "\n"
    return dedent(
        f"""
        Трибуты!

        Наш турнир подошел к концу.
        Вы все проявили невероятную силу, стратегию и волю к победе.
        Пришло время объявить результаты и чествовать наших чемпионов.

        {winners_str}

        Вы показали высший класс в этом турнире, и ваши достижения навсегда останутся в истории наших битв.
        Вся информация о результатах турнира доступна по этой ссылке: {tournament_url}

        Мы благодарим всех участников за их усердие и боевой дух.
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
