from configparser import NoOptionError
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional

from db.global_settings import settings_db
from db.ratings import Rating
from parameters import Parameters
from parameters.bool_param import BoolParam
from parameters.int_param import IntParam
from parameters.str_param import StrParam
from tournament.player import Player


class RegistrationRow(Parameters):
    def __init__(self):
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.tg_id: IntParam = IntParam("ТГ ID")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: IntParam = IntParam("Рейтинг")

    @classmethod
    def from_rating(cls, rating: Rating):
        parameters = cls()
        parameters.tg_username = rating.tg_username
        parameters.tg_id = rating.tg_id
        parameters.nmd_username = rating.nmd_username
        parameters.rating = rating.rating
        return parameters


class Match(Parameters):
    class MatchResult(Enum):
        NotPlayed = 0
        FirstWon = 1
        SecondWon = 2

        def reversed(self):
            if self.value == self.FirstWon:
                return self.SecondWon
            if self.value == self.SecondWon:
                return self.FirstWon
            return self.value

    def __init__(self):
        self.first: StrParam = StrParam("Первый игрок")
        self.first_id: int = 0
        self._result: StrParam = StrParam("Результат")
        self._result_enum: Match.MatchResult = Match.MatchResult.NotPlayed
        self.second_id: int = 0
        self.second: StrParam = StrParam("Второй игрок")
        self.map: StrParam = StrParam("Карта")
        self.battleground_effect: StrParam = StrParam("Эффект поля")

    def to_string(self):
        return f"{self.first.value} {self._result.value} {self.second.value}"

    MATCH_RESULT_TO_STR = {
        MatchResult.NotPlayed: "-",
        MatchResult.FirstWon: "1:0",
        MatchResult.SecondWon: "0:1",
    }
    STR_TO_MATCH_RESULT = {value: key for (key, value) in MATCH_RESULT_TO_STR.items()}

    @property
    def result(self) -> MatchResult:
        return self._result_enum

    @result.setter
    def result(self, new_result: MatchResult):
        self._result_enum = new_result
        self._result.value = Match.MATCH_RESULT_TO_STR[new_result]

    @property
    def result_str(self) -> str:
        return self._result.value

    @result_str.setter
    def result_str(self, new_result: str):
        self._result.value = new_result
        self._result_enum = Match.STR_TO_MATCH_RESULT[new_result]

    @classmethod
    def new_match(cls, player: RegistrationRow, opponent: Optional[RegistrationRow]):
        player_name = player.tg_username.value
        if player.nmd_username.value:
            player_name = player_name + f"({player.nmd_username.value})"
        opponent_name = ""
        if opponent:
            opponent_name = opponent.nmd_username.value
            if opponent.nmd_username.value:
                opponent_name = opponent_name + f"({opponent.nmd_username.value})"
        match = cls.from_row([player_name, "", opponent_name])
        match.result = cls.MatchResult.NotPlayed
        return match


class Result(Parameters):
    def __init__(self):
        self.place: IntParam = IntParam("Место")
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: IntParam = IntParam("Рейтинг")
        self.mm: IntParam = IntParam("Очки")
        self.sos: IntParam = IntParam("SOS")
        self.sodos: IntParam = IntParam("SODOS")

    @classmethod
    def create(cls, place: int, player: Player, user: RegistrationRow):
        res = cls.from_row(
            [
                place,
                user.tg_username,
                user.nmd_username,
                player.rating,
                player.mm,
                player.sos,
                player.sodos,
            ]
        )
        return res


class TournamentSettings(Parameters):
    DATETIME_FORMAT = "%d/%m/%Y, %H:%M"

    def __init__(self):
        self.rounds_number: IntParam = IntParam("Количество раундов")
        self.registration_duration_hours: IntParam = IntParam(
            "Длительность регистрации в часах"
        )
        self.round_duration_hours: IntParam = IntParam("Длительность раунда в часах")
        self.nightmare_matches: IntParam = IntParam("Количество Nightmare матчей")
        self.dangerous_matches: IntParam = IntParam("Количество Dangerous матчей")
        self.element_effect_map: BoolParam = BoolParam("Элементные слабости на поле")
        self.registration_list_message_id: IntParam = IntParam(
            "ID сообщения зарегистрированных игроков"
        )
        self._tournament_start_date = StrParam("Время начала турнира")

    @property
    def round_duration_seconds(self) -> float:
        return timedelta(hours=self.round_duration_hours.value).total_seconds()

    @property
    def registration_duration_seconds(self) -> float:
        return timedelta(hours=self.registration_duration_hours.value).total_seconds()

    @property
    def tournament_start_date(self) -> datetime:
        datestr = self._tournament_start_date.value
        return datetime.strptime(datestr, self.DATETIME_FORMAT)

    @tournament_start_date.setter
    def tournament_start_date(self, new_date: datetime):
        datestr = new_date.strftime(self.DATETIME_FORMAT)
        self._tournament_start_date.value = datestr

    @property
    def tournament_finish_datetime(self) -> datetime:
        tournament_duration = (
            self.rounds_number.value * self.round_duration_hours.value
            + self.registration_duration_hours.value
        )
        return self.tournament_start_date + timedelta(hours=tournament_duration)

    @classmethod
    def default_settings(cls):
        settings = cls()
        for name, param in settings.params().items():
            try:
                param.set_value(settings_db.settings.get_value(name))
            except NoOptionError:
                pass
        return settings
