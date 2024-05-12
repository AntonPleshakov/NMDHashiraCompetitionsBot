from typing import List

from config.config import getconf
from db.tournament_structures import RegistrationRow


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
        self.mm: float = rating / 100
        self.sos: float = 0
        self.sodos: float = 0

    @classmethod
    def from_registration(cls, registration: RegistrationRow):
        player = cls(
            registration.tg_id.value,
            registration.rating.value,
            registration.deviation.value,
        )
        return player
