import os
from datetime import date, datetime
from typing import List, Optional, Set

from config.config import getconf
from logger.NMDLogger import nmd_logger
from nmd_exceptions import (
    PlayerNotFoundError,
    TournamentNotStartedError,
    TournamentNotFinishedError,
)
from .gapi.gsheets_manager import GSheetsManager
from .gapi.spreadsheet_manager import SpreadsheetManager
from .gapi.worksheet_manager import WorksheetManager
from .tournament_structures import RegistrationRow, Match, Result, TournamentSettings


class TournamentDB:
    def __init__(self, spreadsheet_manager: SpreadsheetManager):
        self._manager: SpreadsheetManager = spreadsheet_manager
        settings_page_name = getconf("TOURNAMENT_SETTINGS_PAGE_NAME")
        self._settings_page = self._manager.get_worksheet(settings_page_name)
        self._settings: TournamentSettings = TournamentSettings.from_matrix(
            self._settings_page.get_all_values()
        )
        self._registration_page: WorksheetManager = self._manager.get_worksheet(
            getconf("TOURNAMENT_REGISTER_PAGE_NAME")
        )
        self._tours: List[WorksheetManager] = []
        self._results_page: Optional[WorksheetManager] = None
        self._registered_players: Set[int] = set()
        self._restore_tournament()

    @classmethod
    def create_new_tournament(cls, settings: TournamentSettings):
        nmd_logger.info(f"DB: create new tournament")
        spreadsheet_name = (
            getconf("TOURNAMENT_GTABLE_NAME") + " " + date.today().strftime("%d.%m.%Y")
        )
        manager = GSheetsManager().create(spreadsheet_name)
        if os.getenv("MODE") == "Release":
            manager.make_public()
        settings_page = manager.rename_worksheet(
            getconf("TOURNAMENT_SETTINGS_PAGE_NAME")
        )
        settings.tournament_start_date = datetime.now()
        settings_page.update_values(settings.to_matrix())
        registration_page = manager.add_worksheet(
            getconf("TOURNAMENT_REGISTER_PAGE_NAME")
        )
        registration_page.set_header([RegistrationRow().params_views()])
        registration_page.hide_column(RegistrationRow().tg_id.index)
        settings_page.hide_worksheet()
        return cls(manager)

    @classmethod
    def get_latest_tournament(cls):
        conf_ss_name = getconf("TOURNAMENT_GTABLE_NAME")
        manager = GSheetsManager()
        tournaments_ss = [
            ss for ss in manager.get_spreadsheets() if conf_ss_name in ss.name
        ]
        if not tournaments_ss:
            nmd_logger.info("No tournament spreadsheet exist")
            return None

        latest_date = None
        latest_ss = None
        for ss in tournaments_ss:
            date_list = ss.name.split()[-1].split(".")
            ss_date = date(int(date_list[2]), int(date_list[1]), int(date_list[0]))
            if latest_date is None or latest_date < ss_date:
                latest_date = ss_date
                latest_ss = ss
        ss = manager.open(latest_ss.id)
        return TournamentDB(ss)

    def _restore_tournament(self):
        for player in self.get_registered_players():
            self._registered_players.add(player.tg_id.value)

        tour_number = 1
        tour_title = getconf("TOURNAMENT_TOUR_PAGE_NAME") + " " + str(tour_number)
        while self._manager.is_worksheet_exist(tour_title):
            tour_page = self._manager.get_worksheet(tour_title)
            self._tours.append(tour_page)
            tour_number += 1
            tour_title = getconf("TOURNAMENT_TOUR_PAGE_NAME") + " " + str(tour_number)

    def get_url(self):
        return self._manager.get_url()

    def register_player(self, player: RegistrationRow):
        nmd_logger.info(f"DB: register player {player.tg_username.value}")
        self._registration_page.add_row(player.to_row())
        self._registration_page.sort_table(player.rating.index)
        self._registered_players.add(player.tg_id.value)

    def get_registered_players(self) -> List[RegistrationRow]:
        matrix = self._registration_page.get_all_values()
        players = [RegistrationRow.from_row(row) for row in matrix]
        return players

    def is_player_registered(self, player_tg_id: int) -> bool:
        return player_tg_id in self._registered_players

    def update_player_info(self, player: RegistrationRow):
        nmd_logger.info(f"DB: update player info to: {', '.join(player.to_row())}")
        players = self.get_registered_players()
        player_indexes = [
            i for i, v in enumerate(players) if v.tg_username == player.tg_username
        ]
        if not player_indexes:
            nmd_logger.warning("DB: Player not found")
            raise PlayerNotFoundError
        row = player_indexes[0] + 2  # starting from 1 plus header
        start_range = (row, 1)
        self._registration_page.update_values(
            [player.to_row()], start_range=start_range
        )
        self._registration_page.sort_table(player.rating.index)

    def start_new_tour(self, pairs: List[Match]):
        nmd_logger.info("DB: start new tour")
        tour_number = len(self._tours) + 1
        tour_title = getconf("TOURNAMENT_TOUR_PAGE_NAME") + " " + str(tour_number)
        tour_page = self._manager.add_worksheet(tour_title)
        tour_page.set_header([Match().params_views()])
        tour_page.hide_column(Match().first_id.index)
        tour_page.hide_column(Match().second_id.index)
        matrix = [match.to_row() for match in pairs]
        tour_page.update_values(matrix)
        self._tours.append(tour_page)

    def register_result(self, pair_index: int, result: str):
        nmd_logger.info(f"DB: register result. Pair {pair_index}, result {result}")
        if not self._tours:
            raise TournamentNotStartedError
        tour = self._tours[-1]
        start_range = (pair_index + 2, Match()._result.index + 1)
        tour.update_values([[result]], start_range=start_range)

    def get_results(self, tour_idx: int = -1) -> List[Match]:
        if not self._tours:
            raise TournamentNotStartedError
        tour = self._tours[tour_idx]
        matrix = tour.get_all_values()
        results = [Match.from_row(row) for row in matrix]
        return results

    def get_final_results(self) -> List[Result]:
        if not self.is_finished():
            raise TournamentNotFinishedError
        matrix = self._results_page.get_all_values()
        results = [Result.from_row(row) for row in matrix]
        return results

    def get_tours_number(self) -> int:
        return len(self._tours)

    def finish_tournament(self, tournament_table: List[Result]):
        nmd_logger.info("DB: finish tournament")
        results_title = getconf("TOURNAMENT_RESULTS_PAGE_NAME")
        results_page = self._manager.add_worksheet(results_title)
        results_page.set_header([Result().params_views()])
        matrix = [player.to_row() for player in tournament_table]
        results_page.update_values(matrix)
        self._results_page = results_page

    def is_finished(self) -> bool:
        return self._results_page is not None

    @property
    def settings(self) -> TournamentSettings:
        return self._settings

    @settings.setter
    def settings(self, value: TournamentSettings):
        self._settings = value
        self._settings_page.update_values(value.to_matrix())
