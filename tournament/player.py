from enum import Enum
from typing import List

from config.config import getconf


class ColumnIndexes(Enum):
    TG_USERNAME = 0
    NMD_USERNAME = 1
    RATING = 2
    DEVIATION = 3


class Player:
    def __init__(
        self,
        tg_username: str,
        nmd_username: str = "",
        rating: int = 100,
        deviation: int = getconf("DEFAULT_K"),
    ):
        self.tg_username: str = tg_username
        self.nmd_username: str = nmd_username
        self.rating: int = rating
        self.deviation: int = deviation

    def __eq__(self, other):
        tg = self.tg_username == other.tg_username
        nmd = self.nmd_username == other.nmd_username
        rating = self.rating == other.rating
        dev = self.deviation == other.deviation
        return tg and nmd and rating and dev

    def to_list(self) -> List[str]:
        row = [""] * len(ColumnIndexes)
        row[ColumnIndexes.TG_USERNAME.value] = self.tg_username
        row[ColumnIndexes.NMD_USERNAME.value] = self.nmd_username
        row[ColumnIndexes.RATING.value] = str(self.rating)
        row[ColumnIndexes.DEVIATION.value] = str(self.deviation)
        return row

    @classmethod
    def from_list(cls, values: List[str]):
        tg_username = values[ColumnIndexes.TG_USERNAME.value]
        nmd_username = values[ColumnIndexes.NMD_USERNAME.value]
        rating = int(values[ColumnIndexes.RATING.value])
        deviation = int(values[ColumnIndexes.DEVIATION.value])
        return cls(tg_username, nmd_username, rating, deviation)
