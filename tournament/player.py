from math import floor
from typing import Set, Dict

from db.tournament_structures import RegistrationRow, Result, Match


class Player:
    def __init__(
        self,
        tg_id: int,
        rating: int = 100,
    ):
        self.tg_id: int = tg_id
        self.rating: int = rating
        self.opponents: Set[int] = set()
        self.results: Dict[int, Match.MatchResult] = {}
        self.had_bye: bool = False
        self.mm: int = floor(rating / 100)
        self.sos: float = 0
        self.sodos: float = 0

    @classmethod
    def from_registration(cls, registration: RegistrationRow):
        player = cls(
            registration.tg_id.value,
            registration.rating.value,
        )
        return player

    def to_result(self, place: int, user: RegistrationRow) -> Result:
        res = Result.from_row(
            [
                place,
                user.tg_username.value,
                user.tg_id.value,
                user.nmd_username.value,
                self.rating,
                self.mm,
                self.sos,
                self.sodos,
            ]
        )
        return res
