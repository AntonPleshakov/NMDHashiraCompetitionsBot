from typing import List

from db.tournament_db import TournamentDB
from match import Match, MatchResult
from player import Player


class Tournament:
    @classmethod
    def new_tournament(cls):
        db = TournamentDB.create_new_tournament()
        return cls(db)

    @classmethod
    def current_tournament(cls):
        db = TournamentDB.get_latest_tournament()
        if not db.is_finished():
            return None
        return cls(db)

    def __init__(self, db: TournamentDB):
        self._db = db

    def _generate_pairs(self) -> List[Match]:
        pass

    def new_round(self):
        pass

    def add_player(self, player: Player):
        pass

    def add_result(self, players: List[Player], result: MatchResult):
        pass

    def finish_tournament(self):
        pass
