from math import floor
from typing import Set, Dict, List

from db.ratings import Rating
from db.tournament_structures import RegistrationRow, Result, Match
from nmd_exceptions import NewPlayerError


class Player:
    def __init__(
        self,
        tg_id: int,
        username: str,
        rating: int,
        deviation: int,
        weeks_to_last_tournament: int,
    ):
        self.tg_id: int = tg_id
        self.username: str = username
        self.rating: int = rating
        self.deviation: int = deviation
        self.weeks_to_last_tournament: int = weeks_to_last_tournament

        self.opponents: List[Player] = []
        self.opponents_ids: Set[int] = set()
        self.results: Dict[int, Match.MatchResult] = {}
        self.had_bye: bool = False
        self.mm: int = floor(rating / 100)
        self.sos: float = 0
        self.sodos: float = 0

        # unused, for rating formulas
        self.handicap: int = 0

    @classmethod
    def from_rating(cls, rating: Rating):
        try:
            weeks_to_last_tournament = rating.get_weeks()
        except NewPlayerError:
            weeks_to_last_tournament = -1

        username = rating.nmd_username.value
        if not username:
            username = rating.tg_username.value

        player = cls(
            rating.tg_id.value,
            username,
            rating.rating.value,
            rating.deviation.value,
            weeks_to_last_tournament,
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

    def add_opponent(self, player):
        self.opponents_ids.add(player.tg_id)
        self.opponents.append(player)
