import threading
from datetime import timedelta, datetime
from typing import Optional

from db.global_settings import settings_db
from db.tournament import TournamentDB
from db.tournament_structures import TournamentSettings
from main import bot
from nmd_exceptions import TournamentNotStartedError
from tg.tournament.finish import announce_tournament_end
from tg.tournament.new_tour import announce_new_tour
from tg.tournament.start_new import start_new_tournament
from .tournament import Tournament, TournamentState


class TournamentManager:
    def __init__(self):
        self._tournament: Optional[Tournament] = None
        self._settings: TournamentSettings = TournamentSettings.default_settings()
        self._restore_tournament()

    def _restore_tournament(self):
        latest_tournament_db = TournamentDB.get_latest_tournament()
        if not latest_tournament_db:
            return

        if latest_tournament_db.is_finished():
            settings = settings_db.settings
            if settings.auto_tournament_enabled.value:
                days_period: int = settings.tournaments_days_period.value
                last_date: datetime = (
                    latest_tournament_db.settings.tournament_finish_datetime
                )
                next_date: datetime = last_date + timedelta(days=days_period)
                while next_date < datetime.now():
                    next_date += timedelta(days=days_period)
                diff_to_next_date: timedelta = next_date - datetime.now()
                seconds_to_next_date = diff_to_next_date.total_seconds()
                threading.Timer(
                    seconds_to_next_date,
                    start_new_tournament,
                    [bot, TournamentSettings.default_settings()],
                ).start()
        else:
            self._tournament = Tournament(latest_tournament_db)
            self._settings = self._tournament.db.settings

            registration_duration = self._settings.registration_duration_hours.value
            last_date = self._settings.tournament_start_date
            next_date = last_date + timedelta(hours=registration_duration)
            if self._tournament.state != TournamentState.REGISTRATION:
                for i in range(self._settings.rounds_number.value):
                    round_duration = self._settings.round_duration_hours.value
                    next_date += timedelta(hours=round_duration)
            if next_date > datetime.now():
                diff: timedelta = next_date - datetime.now()
                threading.Timer(
                    diff.total_seconds(),
                    TournamentManager.next_tour,
                    [self],
                ).start()
            else:
                # error
                pass

    @property
    def tournament(self):
        if not self._tournament:
            raise TournamentNotStartedError
        return self._tournament

    def start_tournament(self, settings: TournamentSettings):
        self._tournament = Tournament(TournamentDB.create_new_tournament(settings))
        self._settings = settings
        threading.Timer(
            settings.registration_duration_seconds, TournamentManager.next_tour, [self]
        ).start()

    def next_tour(self):
        if not self._tournament:
            raise TournamentNotStartedError
        if self._tournament.db.get_tours_number() < self._settings.rounds_number.value:
            pairs = self._tournament.new_round()
            announce_new_tour(pairs)
            round_duration = self._settings.round_duration_seconds
            threading.Timer(round_duration, TournamentManager.next_tour, [self]).start()
        else:
            self._finish_tournament()

    def _finish_tournament(self):
        self._tournament.finish_tournament()
        announce_tournament_end(bot)
        self._tournament = None
        settings = settings_db.settings
        if settings.auto_tournament_enabled.value:
            next_tournament_duration = (
                settings.tournaments_days_period.value * 24 * 60 * 60
            )
            threading.Timer(
                next_tournament_duration,
                start_new_tournament,
                [bot, TournamentSettings.default_settings()],
            ).start()


tournament_manager = TournamentManager()
