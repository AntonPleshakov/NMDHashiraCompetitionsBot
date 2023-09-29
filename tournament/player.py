from enum import Enum
from typing import List

from config.config import getconf


class PlayerColumnIndexes(Enum):
    TG_USERNAME = 0
    NMD_USERNAME = 1
    RATING = 2
    DEVIATION = 3


class Player:
    PLAYER_FIELDS = ["ТГ Username", "NMD Username", "Рейтинг", "Отклонение"]

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
        self.opponents: List[str] = []
        self.mm: float = 1
        self.sos: float = 0
        self.sodos: float = 0

    def __eq__(self, other):
        tg = self.tg_username == other.tg_username
        nmd = self.nmd_username == other.nmd_username
        rating = self.rating == other.rating
        dev = self.deviation == other.deviation
        return tg and nmd and rating and dev

    def to_list(self) -> List[str]:
        row = [""] * len(PlayerColumnIndexes)
        row[PlayerColumnIndexes.TG_USERNAME.value] = self.tg_username
        row[PlayerColumnIndexes.NMD_USERNAME.value] = self.nmd_username
        row[PlayerColumnIndexes.RATING.value] = str(self.rating)
        row[PlayerColumnIndexes.DEVIATION.value] = str(self.deviation)
        return row

    @classmethod
    def from_list(cls, values: List[str]):
        tg_username = values[PlayerColumnIndexes.TG_USERNAME.value]
        nmd_username = values[PlayerColumnIndexes.NMD_USERNAME.value]
        rating = int(values[PlayerColumnIndexes.RATING.value])
        deviation = int(values[PlayerColumnIndexes.DEVIATION.value])
        return cls(tg_username, nmd_username, rating, deviation)
