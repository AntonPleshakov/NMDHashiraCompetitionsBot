import threading
from typing import Optional

from db.tournament import TournamentDB
from nmd_exceptions import TournamentNotStartedError
from .tournament import Tournament
from .tournament_settings import TournamentSettings


class TournamentManager:
    def __init__(self):
        self._tournament: Optional[Tournament] = None
        latest_tournament_db = TournamentDB.get_latest_tournament()
        if latest_tournament_db and not latest_tournament_db.is_finished():
            self._tournament = Tournament(latest_tournament_db)
        self._settings: TournamentSettings = TournamentSettings()

    @property
    def tournament(self):
        if not self._tournament:
            raise TournamentNotStartedError
        return self._tournament

    def start_tournament(self, settings: TournamentSettings):
        self._tournament = Tournament(TournamentDB.create_new_tournament(settings))
        self._settings = settings
        threading.Timer(
            settings.round_duration_seconds, TournamentManager.next_tour, [self]
        ).start()

    def next_tour(self):
        if not self._tournament:
            raise TournamentNotStartedError
        if self._tournament.db.get_tours_number() < self._settings.rounds_number.value:
            self._tournament.new_round()
            round_duration = self._settings.round_duration_seconds
            threading.Timer(round_duration, TournamentManager.next_tour, [self]).start()
        else:
            self._tournament.finish_tournament()
            self._tournament = None


tournament_manager = TournamentManager()
