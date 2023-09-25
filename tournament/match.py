from enum import Enum
from typing import List

from tournament.player import Player


class MatchResult(Enum):
    Tie = 0
    NotPlayed = 1
    FirstWon = 2
    SecondWon = 3


MATCH_RESULT_TO_STR = {
    MatchResult.NotPlayed: "",
    MatchResult.Tie: "Ничья",
    MatchResult.FirstWon: "1:0",
    MatchResult.SecondWon: "0:1",
}
STR_TO_MATCH_RESULT = {value: key for (key, value) in MATCH_RESULT_TO_STR.items()}


class MatchColumnIndexes(Enum):
    FIRST_PLAYER = 0
    SECOND_PLAYER = 1
    RESULT = 2


class Match:
    MATCH_FIELDS = ["Первый игрок", "Второй игрок", "Результат"]

    def __init__(self, first_player: Player, second_player: Player):
        self.first_player: Player = first_player
        self.second_player: Player = second_player
        self.result: MatchResult = MatchResult.NotPlayed

    def to_list(self) -> List[str]:
        row = [""] * len(MatchColumnIndexes)
        row[MatchColumnIndexes.FIRST_PLAYER.value] = self.first_player.nmd_username
        row[MatchColumnIndexes.SECOND_PLAYER.value] = self.second_player.nmd_username
        row[MatchColumnIndexes.RESULT.value] = MATCH_RESULT_TO_STR[self.result]
        return row

    @classmethod
    def from_list(cls, values: List[str]):
        first_player = Player("", values[MatchColumnIndexes.FIRST_PLAYER.value])
        second_player = Player("", values[MatchColumnIndexes.SECOND_PLAYER.value])
        match = cls(first_player, second_player)
        str_result = (
            values[MatchColumnIndexes.RESULT.value]
            if len(values) == len(MatchColumnIndexes)
            else ""
        )
        match.result = STR_TO_MATCH_RESULT[str_result]
        return match
