from typing import Set

from db.tournament_structures import RegistrationRow, Result


class Player:
    def __init__(
        self,
        tg_id: int,
        rating: int = 100,
    ):
        self.tg_id: int = tg_id
        self.rating: int = rating
        self.opponents: Set[int] = set()
        self.mm: float = rating / 100
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
                user.tg_username,
                user.nmd_username,
                self.rating,
                self.mm,
                self.sos,
                self.sodos,
            ]
        )
        return res
