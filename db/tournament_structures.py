from enum import Enum
from typing import Optional

from db.ratings import Rating
from parameters import Parameters
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
