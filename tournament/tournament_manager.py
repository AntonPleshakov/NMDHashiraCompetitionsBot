from datetime import timedelta, datetime
from typing import Optional

from common.nmd_datetime import nmd_now
from db.global_settings import settings_db
from db.tournament import TournamentDB
from db.tournament_structures import TournamentSettings
from logger.NMDLogger import nmd_logger
from main import bot
from nmd_exceptions import TournamentNotStartedError
from tg.tournament.announcements import (
    start_new_tournament,
    announce_tournament_end,
    announce_new_tour,
    announce_tournament_end_without_players,
)
from tg.utils import tournament_timer
from .tournament import Tournament, TournamentState


class TournamentManager:
    def __init__(self):
        nmd_logger.info(f"Tournament manager created")
        self._tournament: Optional[Tournament] = None
        self._settings: TournamentSettings = TournamentSettings.default_settings()
        self._restore_tournament()

    def _restore_tournament(self):
        nmd_logger.info("Try to restore tournament")
        latest_tournament_db = TournamentDB.get_latest_tournament()
        if not latest_tournament_db:
            nmd_logger.info("No tournaments exists")
            return

        now = nmd_now()
        if latest_tournament_db.is_finished():
            nmd_logger.info("No tournaments in progress")
            settings = settings_db.settings
            if settings.auto_tournament_enabled.value:
                days_period: int = settings.tournaments_days_period.value
                last_date: datetime = (
                    latest_tournament_db.settings.tournament_finish_datetime
                )
                next_date: datetime = last_date + timedelta(days=days_period)
                while next_date < now:
                    next_date += timedelta(days=days_period)
                diff_to_next_date: timedelta = next_date - now
                seconds_to_next_date = diff_to_next_date.total_seconds()
                tournament_timer.update_timer(
                    seconds_to_next_date,
                    start_new_tournament,
                    [bot, TournamentSettings.default_settings()],
                ).start()
                nmd_logger.info(
                    f"Next tournament will start in {seconds_to_next_date} seconds (in {next_date})"
                )
        else:
            self._tournament = Tournament(latest_tournament_db)
            self._settings = self._tournament.db.settings
            nmd_logger.info(
                f"We have tournament in state {self._tournament.state.name}"
            )

            registration_duration = self._settings.registration_duration_hours.value
            last_date = self._settings.tournament_start_date
            next_date = last_date + timedelta(hours=registration_duration)
            print(
                f"next_date: {next_date}; registration_duration: {registration_duration}; last_date: {last_date}; timedelta: {timedelta(hours=registration_duration)}"
            )
            if self._tournament.state != TournamentState.REGISTRATION:
                for i in range(self._tournament.db.get_tours_number()):
                    round_duration = self._settings.round_duration_hours.value
                    next_date += timedelta(hours=round_duration)
            if next_date > now:
                diff: timedelta = next_date - now
                tournament_timer.update_timer(
                    diff.total_seconds(),
                    TournamentManager.next_tour,
                    [self],
                ).start()
                nmd_logger.info(
                    f"Next tour will start in {diff.total_seconds()} seconds (in {next_date})"
                )
            else:
                nmd_logger.error("Bot was unavailable longer than a tour duration")
                self.next_tour()

    @property
    def tournament(self):
        if not self._tournament:
            nmd_logger.info("Try to get not started tournament, exception")
            raise TournamentNotStartedError
        return self._tournament

    def start_tournament(self, settings: TournamentSettings):
        nmd_logger.info("Start new tournament")
        self._tournament = Tournament(TournamentDB.create_new_tournament(settings))
        self._settings = settings
        start_new_tournament(settings, self._tournament.db, bot)
        tournament_timer.update_timer(
            settings.registration_duration_seconds, TournamentManager.next_tour, [self]
        ).start()
        nmd_logger.info(
            f"First tour will start in {settings.registration_duration_seconds} seconds"
        )

    def next_tour(self):
        nmd_logger.info("Start next tour")
        if not self._tournament:
            nmd_logger.exception(
                "Try to start next tour when no tournaments in progress, exception"
            )
            raise TournamentNotStartedError
        if self._tournament.db.get_tours_number() < self._settings.rounds_number.value:
            try:
                pairs = self._tournament.new_round()
            except Exception as e:
                nmd_logger.info(f"Exception in pairing. Finish tournament. {e}")
                self._finish_tournament(False)
                return
            announce_new_tour(pairs, self._tournament.db, bot)
            round_duration = self._settings.round_duration_seconds
            tournament_timer.update_timer(
                round_duration, TournamentManager.next_tour, [self]
            ).start()
            nmd_logger.info(f"Next tour will start in {round_duration} seconds")
        else:
            nmd_logger.info("Last tour finished")
            self._finish_tournament(True)

    def _finish_tournament(self, should_update_coefficients):
        nmd_logger.info("Finish tournament")
        try:
            self.tournament.finish_tournament(should_update_coefficients)
            announce_tournament_end(self.tournament.db, bot)
        except TournamentNotStartedError:
            announce_tournament_end_without_players(self.tournament.db, bot)
        self._tournament = None
        settings = settings_db.settings
        if settings.auto_tournament_enabled.value:
            now = nmd_now()
            next_tournament_day = now + timedelta(
                days=settings.tournaments_days_period.value
            )
            next_tournament_day = next_tournament_day.replace(
                hour=settings.tournament_start_time_hours.value,
                minute=settings.tournament_start_time_minutes.value,
            )

            next_tournament_duration = next_tournament_day - now
            tournament_timer.update_timer(
                next_tournament_duration.total_seconds(),
                start_new_tournament,
                [bot, TournamentSettings.default_settings()],
            ).start()
            nmd_logger.info(
                f"Next tournament will start in {next_tournament_duration} seconds"
            )
        else:
            nmd_logger.info("Auto tournament start is disabled")


tournament_manager = TournamentManager()
