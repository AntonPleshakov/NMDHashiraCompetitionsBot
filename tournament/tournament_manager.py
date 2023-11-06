import datetime
import threading
from typing import Optional

from db.tournament_db import TournamentDB
from tournament.tournament import Tournament


class TournamentSettings:
    rounds_number = 5
    round_duration_hours = 24
    nightmare_matches = 0
    dangerous_matches = 2
    element_effect_map_disabled = True

    def round_duration_seconds(self) -> int:
        return datetime.timedelta(hours=self.round_duration_hours).seconds


class TournamentManager:
    def __init__(self):
        self.tournament: Optional[Tournament] = None
        latest_tournament_db = TournamentDB.get_latest_tournament()
        if latest_tournament_db and not latest_tournament_db.is_finished():
            self.tournament = Tournament(latest_tournament_db)
        self._settings: TournamentSettings = TournamentSettings()

    def start_tournament(self, settings: TournamentSettings):
        self.tournament = Tournament(TournamentDB.create_new_tournament())
        self._settings = settings
        threading.Timer(
            settings.round_duration_seconds(), TournamentManager.next_tour, [self]
        ).start()

    def next_tour(self):
        if self.tournament.db.get_tours_number() < self._settings.rounds_number:
            self.tournament.new_round()
            round_duration = self._settings.round_duration_seconds()
            threading.Timer(round_duration, TournamentManager.next_tour, [self]).start()
        else:
            self.tournament.finish_tournament()
            self.tournament = None