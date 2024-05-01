from typing import List

from config.config import getconf
from db.ratings import Rating


class Player:
    def __init__(
        self,
        tg_id: int,
        rating: int = 100,
        deviation: int = getconf("DEFAULT_K"),
    ):
        self.tg_id: int = tg_id
        self.rating: int = rating
        self.deviation: int = deviation
        self.opponents: List[int] = []
        self.mm: float = 1
        self.sos: float = 0
        self.sodos: float = 0
