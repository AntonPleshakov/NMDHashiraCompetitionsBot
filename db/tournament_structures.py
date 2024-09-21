from datetime import datetime, timedelta
from enum import Enum
from typing import List

from common.nmd_datetime import nmd_parse_datetime
from db.global_settings import settings_db
from db.ratings import Rating
from parameters import Parameters
from parameters.int_param import IntParam
from parameters.str_param import StrParam


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
            if self == self.FirstWon:
                return self.SecondWon
            if self == self.SecondWon:
                return self.FirstWon
            return self

    def __init__(self):
        self.first: StrParam = StrParam("Первый игрок")
        self.first_id: IntParam = IntParam("ТГ ID")
        self._result: StrParam = StrParam("Результат")
        self._result_enum: Match.MatchResult = Match.MatchResult.NotPlayed
        self.second: StrParam = StrParam("Второй игрок")
        self.second_id: IntParam = IntParam("ТГ ID")
        self.map: StrParam = StrParam("Карта")
        self.rounds: IntParam = IntParam("Раунды")

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
        if Match.STR_TO_MATCH_RESULT[self._result.value] != self._result_enum:
            self._result_enum = Match.STR_TO_MATCH_RESULT[self._result.value]
        return self._result_enum

    @result.setter
    def result(self, new_result: MatchResult):
        self._result_enum = new_result
        self._result.value = Match.MATCH_RESULT_TO_STR[new_result]

    @property
    def result_str(self) -> str:
        return self._result.value

    @classmethod
    def new_match(
        cls,
        player_name: str,
        player_id: int,
        opponent_name: str = "",
        opponent_id: int = 0,
    ):
        match = cls.from_row([player_name, player_id, "", opponent_name, opponent_id])
        match.result = cls.MatchResult.NotPlayed
        return match


class Result(Parameters):
    def __init__(self):
        self.place: IntParam = IntParam("Место")
        self.tg_username: StrParam = StrParam("ТГ Username")
        self.tg_id: IntParam = IntParam("ТГ ID")
        self.nmd_username: StrParam = StrParam("NMD Username")
        self.rating: StrParam = StrParam("Рейтинг")
        self.mm: IntParam = IntParam("Очки")
        self.sos: IntParam = IntParam("SOS")
        self.sodos: IntParam = IntParam("SODOS")


class TournamentSettings(Parameters):
    DATETIME_FORMAT = "%d/%m/%Y, %H:%M"

    def __init__(self):
        self.rounds_number: IntParam = IntParam("Количество раундов")
        self.registration_duration_hours: IntParam = IntParam(
            "Длительность регистрации в часах"
        )
        self.round_duration_hours: IntParam = IntParam("Длительность раунда в часах")
        self.unrivaled_matches: IntParam = IntParam("Количество Unrivaled матчей")
        self.nightmare_matches: IntParam = IntParam("Количество Nightmare матчей")
        self.dangerous_matches: IntParam = IntParam("Количество Dangerous матчей")
        self.bo2_matches: IntParam = IntParam("Количество Bo2 матчей")
        self.registration_list_message_id: IntParam = IntParam(
            "ID сообщения зарегистрированных игроков"
        )
        self.last_tour_message_id: IntParam = IntParam("Last tour message id")
        self._tournament_start_date = StrParam("Время начала турнира")

    @staticmethod
    def private_parameters() -> List[str]:
        return ["registration_list_message_id", "_tournament_start_date"]

    @property
    def round_duration_seconds(self) -> float:
        return timedelta(hours=self.round_duration_hours.value).total_seconds()

    @property
    def registration_duration_seconds(self) -> float:
        return timedelta(hours=self.registration_duration_hours.value).total_seconds()

    @property
    def tournament_start_date(self) -> datetime:
        datestr = self._tournament_start_date.value
        return nmd_parse_datetime(datestr, self.DATETIME_FORMAT)

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
            except AttributeError:
                pass
        return settings
